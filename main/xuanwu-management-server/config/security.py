def resolve_control_secret(config: dict) -> str:
    control_plane_secret = str(config.get("control-plane", {}).get("secret", "")).strip()
    if control_plane_secret:
        return control_plane_secret
    return str(config.get("server", {}).get("auth_key", "")).strip()
