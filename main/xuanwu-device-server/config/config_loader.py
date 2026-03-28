import os
import yaml
from collections.abc import Mapping

from core.control_plane.local_store import LocalControlPlaneStore
from config.manage_api_client import init_service, get_server_config, get_agent_models
from config.xuanwu_management_client import (
    fetch_server_config as fetch_xuanwu_management_server_config,
    is_xuanwu_management_server_enabled,
    resolve_private_config as resolve_xuanwu_management_private_config,
)


def get_project_dir():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"


def read_config(config_path):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def load_bootstrap_config():
    default_config_path = get_project_dir() + "config.yaml"
    custom_config_path = get_project_dir() + "data/.config.yaml"
    default_config = read_config(default_config_path)
    custom_config = read_config(custom_config_path)
    return apply_environment_overrides(merge_configs(default_config, custom_config))


def load_config():
    """加载配置文件"""
    from core.utils.cache.manager import cache_manager, CacheType

    # 检查缓存
    cached_config = cache_manager.get(CacheType.CONFIG, "main_config")
    if cached_config is not None:
        return cached_config

    bootstrap_config = load_bootstrap_config()

    if should_use_dynamic_server_config(bootstrap_config):
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，使用异步版本
            config = asyncio.run_coroutine_threadsafe(
                get_config_from_api_async(bootstrap_config), loop
            ).result()
        except RuntimeError:
            # 如果不在事件循环中（启动时），创建新的事件循环
            config = asyncio.run(get_config_from_api_async(bootstrap_config))
    else:
        config = bootstrap_config
    # 初始化目录
    ensure_directories(config)

    # 缓存配置
    cache_manager.set(CacheType.CONFIG, "main_config", config)
    return config


def apply_environment_overrides(config):
    config = merge_configs({}, config)
    management_config = config.setdefault("xuanwu-management-server", {})
    management_url = os.environ.get("XUANWU_MANAGEMENT_SERVER_URL", "").strip()
    management_secret = os.environ.get("XUANWU_MANAGEMENT_SERVER_SECRET", "").strip()
    management_enabled = os.environ.get("XUANWU_MANAGEMENT_SERVER_ENABLED", "").strip()

    if management_url:
        management_config["url"] = management_url
    if management_secret:
        management_config["secret"] = management_secret
    if management_enabled:
        management_config["enabled"] = management_enabled.lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
    elif management_url or management_secret:
        management_config["enabled"] = True
    return config


async def get_config_from_api_async(config):
    """从动态控制面获取配置（异步版本，优先本地 control-plane）"""
    control_plane_store = _get_local_control_plane_store(config)
    if control_plane_store is not None:
        config_data = control_plane_store.build_server_config(config)
        config_data["read_config_from_api"] = False
        return config_data

    if is_xuanwu_management_server_enabled(config):
        config_data = await fetch_xuanwu_management_server_config(config)
        config_data["read_config_from_api"] = True
        config_data["xuanwu-management-server"] = {
            "url": config["xuanwu-management-server"].get("url", ""),
            "secret": config["xuanwu-management-server"].get("secret", ""),
        }
        auth_enabled = config_data.get("server", {}).get("auth", {}).get("enabled", False)
        if config.get("server"):
            config_data["server"] = {
                **config_data.get("server", {}),
                "ip": config["server"].get("ip", ""),
                "port": config["server"].get("port", ""),
                "http_port": config["server"].get("http_port", ""),
                "vision_explain": config["server"].get("vision_explain", ""),
                "auth_key": config["server"].get("auth_key", ""),
            }
        config_data.setdefault("server", {})
        config_data["server"]["auth"] = {"enabled": auth_enabled}
        if not config_data.get("prompt_template"):
            config_data["prompt_template"] = config.get("prompt_template")
        return config_data

    # 初始化API客户端
    init_service(config)

    # 获取服务器配置
    config_data = await get_server_config()
    if config_data is None:
        raise Exception("Failed to fetch server config from API")

    config_data["read_config_from_api"] = True
    config_data["manager-api"] = {
        "url": config["manager-api"].get("url", ""),
        "secret": config["manager-api"].get("secret", ""),
    }
    auth_enabled = config_data.get("server", {}).get("auth", {}).get("enabled", False)
    # server的配置以本地为准
    if config.get("server"):
        config_data["server"] = {
            "ip": config["server"].get("ip", ""),
            "port": config["server"].get("port", ""),
            "http_port": config["server"].get("http_port", ""),
            "vision_explain": config["server"].get("vision_explain", ""),
            "auth_key": config["server"].get("auth_key", ""),
        }
    config_data["server"]["auth"] = {"enabled": auth_enabled}
    # 如果服务器没有prompt_template，则从本地配置读取
    if not config_data.get("prompt_template"):
        config_data["prompt_template"] = config.get("prompt_template")
    return config_data


async def get_private_config_from_api(config, device_id, client_id):
    """获取运行时私有配置（优先本地 control-plane）"""
    control_plane_store = _get_local_control_plane_store(config)
    if control_plane_store is not None:
        resolved = control_plane_store.resolve_device_config(
            config,
            device_id=device_id,
            client_id=client_id,
            selected_module=None,
        )
        return resolved["resolved_config"]
    if is_xuanwu_management_server_enabled(config):
        return await resolve_xuanwu_management_private_config(
            config,
            device_id,
            client_id,
            config["selected_module"],
        )
    return await get_agent_models(device_id, client_id, config["selected_module"])


def should_use_dynamic_server_config(config):
    return (
        _get_local_control_plane_store(config) is not None
        or is_xuanwu_management_server_enabled(config)
        or is_manager_api_enabled(config)
    )


def should_use_private_config_resolution(config):
    return (
        _get_local_control_plane_store(config) is not None
        or is_xuanwu_management_server_enabled(config)
        or is_manager_api_enabled(config)
    )


def is_manager_api_enabled(config):
    return bool(config.get("manager-api", {}).get("url"))


def resolve_control_secret(config):
    control_plane_config = config.get("control-plane", {})
    server_config = config.get("server", {})
    return (
        control_plane_config.get("secret")
        or server_config.get("runtime_secret")
        or server_config.get("auth_key")
        or config.get("xuanwu-management-server", {}).get("secret", "")
        or config.get("manager-api", {}).get("secret", "")
    )


def _get_local_control_plane_store(config):
    store = LocalControlPlaneStore.from_config(config, project_dir=get_project_dir())
    if not store.control_plane_enabled(config):
        return None
    return store


def ensure_directories(config):
    """确保所有配置路径存在"""
    dirs_to_create = set()
    project_dir = get_project_dir()  # 获取项目根目录
    # 日志文件目录
    log_dir = config.get("log", {}).get("log_dir", "tmp")
    dirs_to_create.add(os.path.join(project_dir, log_dir))

    # ASR/TTS模块输出目录
    for module in ["ASR", "TTS"]:
        if config.get(module) is None:
            continue
        for provider in config.get(module, {}).values():
            output_dir = provider.get("output_dir", "")
            if output_dir:
                dirs_to_create.add(output_dir)

    # 根据selected_module创建模型目录
    selected_modules = config.get("selected_module", {})
    for module_type in ["ASR", "LLM", "TTS"]:
        selected_provider = selected_modules.get(module_type)
        if not selected_provider:
            continue
        if config.get(module) is None:
            continue
        if config.get(selected_provider) is None:
            continue
        provider_config = config.get(module_type, {}).get(selected_provider, {})
        output_dir = provider_config.get("output_dir")
        if output_dir:
            full_model_dir = os.path.join(project_dir, output_dir)
            dirs_to_create.add(full_model_dir)

    # 统一创建目录（保留原data目录创建）
    for dir_path in dirs_to_create:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except PermissionError:
            print(f"警告：无法创建目录 {dir_path}，请检查写入权限")


def merge_configs(default_config, custom_config):
    """
    递归合并配置，custom_config优先级更高

    Args:
        default_config: 默认配置
        custom_config: 用户自定义配置

    Returns:
        合并后的配置
    """
    if not isinstance(default_config, Mapping) or not isinstance(
        custom_config, Mapping
    ):
        return custom_config

    merged = dict(default_config)

    for key, value in custom_config.items():
        if (
            key in merged
            and isinstance(merged[key], Mapping)
            and isinstance(value, Mapping)
        ):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value

    return merged
