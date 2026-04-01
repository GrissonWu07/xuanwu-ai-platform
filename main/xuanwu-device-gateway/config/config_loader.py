import os
from collections.abc import Mapping

import yaml

from config.xuanwu_management_client import (
    fetch_server_config as fetch_xuanwu_management_server_config,
    is_xuanwu_management_server_enabled,
    resolve_private_config as resolve_xuanwu_management_private_config,
)


def get_project_dir():
    """Get the device-server project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"


def read_config(config_path):
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_bootstrap_config():
    default_config_path = get_project_dir() + "config.yaml"
    custom_config_path = get_project_dir() + "data/.config.yaml"
    default_config = read_config(default_config_path)
    custom_config = read_config(custom_config_path)
    return apply_environment_overrides(merge_configs(default_config, custom_config))


def load_config():
    """Load the merged runtime configuration."""
    from core.utils.cache.manager import CacheType, cache_manager

    cached_config = cache_manager.get(CacheType.CONFIG, "main_config")
    if cached_config is not None:
        return cached_config

    bootstrap_config = load_bootstrap_config()
    if should_use_dynamic_server_config(bootstrap_config):
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            config = asyncio.run_coroutine_threadsafe(
                get_config_from_api_async(bootstrap_config), loop
            ).result()
        except RuntimeError:
            config = asyncio.run(get_config_from_api_async(bootstrap_config))
    else:
        config = bootstrap_config

    ensure_directories(config)
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
    """Fetch dynamic server configuration from xuanwu-management-server."""
    if not is_xuanwu_management_server_enabled(config):
        raise RuntimeError(
            "xuanwu-management-server is required for dynamic server config resolution"
        )

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


async def get_private_config_from_api(config, device_id, client_id):
    """Resolve runtime private config from xuanwu-management-server."""
    if not is_xuanwu_management_server_enabled(config):
        raise RuntimeError(
            "xuanwu-management-server is required for runtime private config resolution"
        )
    return await resolve_xuanwu_management_private_config(
        config,
        device_id,
        client_id,
        config["selected_module"],
    )


def should_use_dynamic_server_config(config):
    return is_xuanwu_management_server_enabled(config)


def should_use_private_config_resolution(config):
    return is_xuanwu_management_server_enabled(config)


def resolve_control_secret(config):
    control_plane_config = config.get("control-plane", {})
    server_config = config.get("server", {})
    return (
        control_plane_config.get("secret")
        or server_config.get("runtime_secret")
        or server_config.get("auth_key")
        or config.get("xuanwu-management-server", {}).get("secret", "")
    )


def ensure_directories(config):
    """Ensure configured runtime directories exist."""
    dirs_to_create = set()
    project_dir = get_project_dir()

    log_dir = config.get("log", {}).get("log_dir", "tmp")
    dirs_to_create.add(os.path.join(project_dir, log_dir))

    for module in ["ASR", "TTS"]:
        providers = config.get(module, {})
        if not isinstance(providers, Mapping):
            continue
        for provider in providers.values():
            output_dir = provider.get("output_dir", "")
            if output_dir:
                dirs_to_create.add(output_dir)

    selected_modules = config.get("selected_module", {})
    for module_type in ["ASR", "LLM", "TTS"]:
        selected_provider = selected_modules.get(module_type)
        if not selected_provider:
            continue
        providers = config.get(module_type, {})
        if not isinstance(providers, Mapping):
            continue
        provider_config = providers.get(selected_provider, {})
        output_dir = provider_config.get("output_dir")
        if output_dir:
            dirs_to_create.add(os.path.join(project_dir, output_dir))

    for dir_path in dirs_to_create:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except PermissionError:
            print(f"Warning: unable to create directory {dir_path}")


def merge_configs(default_config, custom_config):
    """Recursively merge config mappings with custom values taking precedence."""
    if not isinstance(default_config, Mapping) or not isinstance(custom_config, Mapping):
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
