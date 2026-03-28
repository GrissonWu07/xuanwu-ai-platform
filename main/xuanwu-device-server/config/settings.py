import os

from config.config_loader import get_project_dir, load_config as load_runtime_config


default_config_file = "config.yaml"
config_file_valid = False


def check_config_file():
    global config_file_valid
    if config_file_valid:
        return

    custom_config_file = get_project_dir() + "data/." + default_config_file
    if not os.path.exists(custom_config_file):
        raise FileNotFoundError(
            "找不到 data/.config.yaml 文件，请按教程确认该配置文件是否存在"
        )

    load_runtime_config()
    config_file_valid = True


def load_config_wrapper():
    check_config_file()
    return load_runtime_config()


load_config = load_config_wrapper
