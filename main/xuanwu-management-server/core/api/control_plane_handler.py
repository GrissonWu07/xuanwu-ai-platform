from __future__ import annotations

import json

from aiohttp import web

from config.security import resolve_control_secret
from core.api.base_handler import BaseHandler
from core.store.base import create_control_plane_store
from core.store.exceptions import DeviceBindException, DeviceNotFoundException


class ControlPlaneHandler(BaseHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        self.store = create_control_plane_store(config)
        self.control_secret = resolve_control_secret(config)

    def _verify_control_secret(self, request: web.Request) -> bool:
        expected = str(self.control_secret or "").strip()
        if not expected:
            return False
        provided = request.headers.get("X-Xuanwu-Control-Secret", "").strip()
        return bool(provided) and provided == expected

    def _json_response(self, payload: dict, *, status: int = 200) -> web.Response:
        response = web.Response(
            text=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            content_type="application/json",
            status=status,
        )
        self._add_cors_headers(response)
        return response

    def _extract_session_token(self, request: web.Request) -> str:
        authorization = str(request.headers.get("Authorization", "")).strip()
        if authorization.lower().startswith("bearer "):
            return authorization[7:].strip()
        return str(request.headers.get("X-Session-Token", "")).strip()

    async def handle_login(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            session = self.store.create_auth_session(payload.get("user_id"), payload.get("password"))
        except ValueError as exc:
            status = 404 if str(exc) == "user_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(session)

    async def handle_logout(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        session_token = str(payload.get("session_token", "")).strip()
        if not session_token:
            return self._json_response({"error": "session_token_required"}, status=400)
        if not self.store.delete_auth_session(session_token):
            return self._json_response({"error": "session_not_found"}, status=404)
        response = web.Response(status=204)
        self._add_cors_headers(response)
        return response

    async def handle_get_me(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        session_token = self._extract_session_token(request)
        if not session_token:
            return self._json_response({"error": "session_token_required"}, status=401)
        payload = self.store.build_auth_me(session_token)
        if payload is None:
            return self._json_response({"error": "session_not_found"}, status=401)
        return self._json_response(payload)

    async def handle_list_roles(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        items = []
        for role in self.store.list_roles():
            normalized = dict(role)
            normalized["permission_count"] = len(normalized.get("permissions") or [])
            items.append(normalized)
        return self._json_response({"items": items})

    async def handle_get_dashboard_overview(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.build_dashboard_overview())

    async def handle_get_portal_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.build_portal_config(self.config))

    async def handle_get_jobs_overview(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.build_jobs_overview())

    async def handle_get_alerts_overview(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.build_alerts_overview())

    async def handle_get_gateway_overview(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.build_gateway_overview())

    async def handle_get_server_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response(self.store.load_server_profile())

    async def handle_put_server_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        return self._json_response(self.store.save_server_profile(payload))

    async def handle_list_users(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_users()})

    async def handle_create_user(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.create_user(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_get_user(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        user_id = request.match_info["user_id"]
        payload = self.store.get_user(user_id)
        if payload is None:
            return self._json_response({"error": "user_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_user(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        user_id = request.match_info["user_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        saved = self.store.save_user(user_id, payload)
        return self._json_response(saved)

    async def handle_delete_user(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        user_id = request.match_info["user_id"]
        if not self.store.delete_user(user_id):
            return self._json_response({"error": "user_not_found"}, status=404)
        response = web.Response(status=204)
        self._add_cors_headers(response)
        return response

    async def handle_list_channels(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_channels()})

    async def handle_create_channel(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.create_channel(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_get_channel(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        channel_id = request.match_info["channel_id"]
        payload = self.store.get_channel(channel_id)
        if payload is None:
            return self._json_response({"error": "channel_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_channel(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        channel_id = request.match_info["channel_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_channel(channel_id, payload)
        except ValueError as exc:
            status = 404 if str(exc) == "channel_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(saved)

    async def handle_delete_channel(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        channel_id = request.match_info["channel_id"]
        if not self.store.delete_channel(channel_id):
            return self._json_response({"error": "channel_not_found"}, status=404)
        response = web.Response(status=204)
        self._add_cors_headers(response)
        return response

    async def handle_list_user_device_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_user_device_mappings()})

    async def handle_create_user_device_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_user_device_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_user_channel_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_user_channel_mappings()})

    async def handle_create_user_channel_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_user_channel_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_channel_device_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_channel_device_mappings()})

    async def handle_create_channel_device_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_channel_device_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_device_agent_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_device_agent_mappings()})

    async def handle_create_device_agent_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.bind_device_agent(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_agent_model_provider_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_agent_model_provider_mappings()})

    async def handle_create_agent_model_provider_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_agent_model_provider_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_agent_model_config_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_agent_model_config_mappings()})

    async def handle_create_agent_model_config_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_agent_model_config_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_agent_knowledge_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_agent_knowledge_mappings()})

    async def handle_create_agent_knowledge_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_agent_knowledge_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_agent_workflow_mappings(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_agent_workflow_mappings()})

    async def handle_create_agent_workflow_mapping(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_agent_workflow_mapping(payload.get("mapping_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_devices(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_devices()})

    async def handle_list_discovered_devices(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_discovered_devices()})

    async def handle_create_discovered_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_discovered_device(payload.get("discovery_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_gateway_device_discovery(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload.setdefault("ingress_type", "gateway")
        try:
            created = self.store.save_discovered_device(payload.get("discovery_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_runtime_device_discovery(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        payload.setdefault("ingress_type", "device_server")
        try:
            created = self.store.save_discovered_device(payload.get("discovery_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_get_discovered_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        discovery_id = str(request.match_info["discovery_id"]).strip()
        payload = self.store.get_discovered_device(discovery_id)
        if payload is None:
            return self._json_response({"error": "discovered_device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_promote_discovered_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        discovery_id = str(request.match_info["discovery_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            promoted = self.store.promote_discovered_device(discovery_id, payload)
        except ValueError as exc:
            status = 404 if str(exc) == "discovered_device_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(promoted)

    async def handle_ignore_discovered_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        discovery_id = str(request.match_info["discovery_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            ignored = self.store.ignore_discovered_device(discovery_id, payload.get("reason"))
        except ValueError as exc:
            status = 404 if str(exc) == "discovered_device_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(ignored)

    async def handle_create_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.save_device(payload.get("device_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_batch_import_devices(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        items = payload.get("items")
        if not isinstance(items, list):
            return self._json_response({"error": "items_required"}, status=400)
        try:
            imported = self.store.batch_import_devices(items)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response({"imported": len(imported), "items": imported}, status=201)

    async def handle_get_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = request.match_info["device_id"]
        payload = self.store.get_device(device_id)
        if payload is None:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_get_device_detail(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        if not device_id:
            return self._json_response({"error": "device_id_required"}, status=400)
        try:
            payload = self.store.build_device_detail(device_id)
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = request.match_info["device_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_device(device_id, payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved)

    async def handle_device_heartbeat(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            updated = self.store.update_device_heartbeat(device_id, payload)
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(updated)

    async def handle_claim_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            claimed = self.store.claim_device(device_id, payload.get("user_id"))
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(claimed)

    async def handle_bind_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            bound = self.store.bind_device(device_id, payload.get("bind_code"))
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(bound)

    async def handle_suspend_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            suspended = self.store.suspend_device(device_id, payload.get("reason"))
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(suspended)

    async def handle_retire_device(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            retired = self.store.retire_device(device_id, payload.get("reason"))
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(retired)

    async def handle_get_agent(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        agent_id = request.match_info["agent_id"]
        payload = self.store.get_agent(agent_id)
        if payload is None:
            return self._json_response({"error": "agent_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_put_agent(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        agent_id = request.match_info["agent_id"]
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        return self._json_response(self.store.save_agent(agent_id, payload))

    async def handle_post_event(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.append_event(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_list_events(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_events(dict(request.query))})

    async def handle_get_event(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        event_id = str(request.match_info["event_id"]).strip()
        payload = self.store.get_event(event_id)
        if payload is None:
            return self._json_response({"error": "event_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_post_telemetry(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            created = self.store.append_telemetry(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(created, status=201)

    async def handle_gateway_event(self, request: web.Request) -> web.Response:
        return await self.handle_post_event(request)

    async def handle_gateway_telemetry(self, request: web.Request) -> web.Response:
        return await self.handle_post_telemetry(request)

    async def handle_gateway_command_result(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            result = self.store.save_command_result(payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(result, status=201)

    async def handle_list_telemetry(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_telemetry(dict(request.query))})

    async def handle_list_alarms(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_alarms()})

    async def handle_get_alarm(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        alarm_id = str(request.match_info["alarm_id"]).strip()
        if not alarm_id:
            return self._json_response({"error": "alarm_id_required"}, status=400)
        payload = self.store.get_alarm(alarm_id)
        if payload is None:
            return self._json_response({"error": "alarm_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_ack_alarm(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        alarm_id = str(request.match_info["alarm_id"]).strip()
        if not alarm_id:
            return self._json_response({"error": "alarm_id_required"}, status=400)
        payload = self.store.acknowledge_alarm(alarm_id)
        if payload is None:
            return self._json_response({"error": "alarm_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_list_gateways(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_gateways()})

    async def handle_get_gateway(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        gateway_id = str(request.match_info["gateway_id"]).strip()
        payload = self.store.get_gateway(gateway_id)
        if payload is None:
            return self._json_response({"error": "gateway_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_upsert_gateway(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        gateway_id = str(request.match_info.get("gateway_id") or "").strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_gateway(gateway_id or payload.get("gateway_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved)

    async def handle_list_capabilities(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_capabilities()})

    async def handle_create_capability(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_capability(payload.get("capability_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_capability_routes(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_capability_routes()})

    async def handle_create_capability_route(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_capability_route(payload.get("route_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_firmwares(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_firmwares()})

    async def handle_get_firmware(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        firmware_id = str(request.match_info["firmware_id"]).strip()
        payload = self.store.get_firmware(firmware_id)
        if payload is None:
            return self._json_response({"error": "firmware_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_upsert_firmware(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        firmware_id = str(request.match_info.get("firmware_id") or "").strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_firmware(firmware_id or payload.get("firmware_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved)

    async def handle_list_ota_campaigns(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_ota_campaigns()})

    async def handle_create_ota_campaign(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_ota_campaign(payload.get("campaign_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_job_schedules(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_schedules()})

    async def handle_get_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        schedule_id = str(request.match_info["schedule_id"]).strip()
        if not schedule_id:
            return self._json_response({"error": "schedule_id_required"}, status=400)
        payload = self.store.get_schedule(schedule_id)
        if payload is None:
            return self._json_response({"error": "schedule_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_create_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            saved = self.store.save_schedule(payload.get("schedule_id"), payload)
        except ValueError as exc:
            return self._json_response({"error": str(exc)}, status=400)
        return self._json_response(saved, status=201)

    async def handle_list_due_job_schedules(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        now_iso = str(request.query.get("now", "")).strip()
        if not now_iso:
            return self._json_response({"error": "now_required"}, status=400)
        limit = int(str(request.query.get("limit", "100")).strip() or "100")
        return self._json_response(
            {"items": self.store.list_due_schedules(now_iso, limit=limit)}
        )

    async def handle_claim_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        schedule_id = str(request.match_info["schedule_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        scheduled_for = str(payload.get("scheduled_for", "")).strip()
        if not scheduled_for:
            return self._json_response({"error": "scheduled_for_required"}, status=400)
        try:
            claimed = self.store.claim_schedule(schedule_id, scheduled_for)
        except ValueError as exc:
            status = 404 if str(exc) == "schedule_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(claimed, status=201)

    async def handle_pause_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        schedule_id = str(request.match_info["schedule_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            paused = self.store.pause_schedule(schedule_id, payload.get("reason"))
        except ValueError as exc:
            status = 404 if str(exc) == "schedule_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(paused)

    async def handle_resume_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        schedule_id = str(request.match_info["schedule_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            resumed = self.store.resume_schedule(schedule_id, payload.get("reason"))
        except ValueError as exc:
            status = 404 if str(exc) == "schedule_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(resumed)

    async def handle_trigger_job_schedule(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        schedule_id = str(request.match_info["schedule_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        scheduled_for = str(payload.get("scheduled_for") or datetime.now(timezone.utc).isoformat()).strip()
        try:
            triggered = self.store.trigger_schedule(schedule_id, scheduled_for)
        except ValueError as exc:
            status = 404 if str(exc) == "schedule_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(triggered, status=201)

    async def handle_list_job_runs(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        return self._json_response({"items": self.store.list_job_runs()})

    async def handle_list_dispatchable_job_runs(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        now_iso = str(request.query.get("now", "")).strip()
        if not now_iso:
            return self._json_response({"error": "now_required"}, status=400)
        limit = int(str(request.query.get("limit", "100")).strip() or "100")
        return self._json_response(
            {"items": self.store.list_dispatchable_job_runs(now_iso, limit=limit)}
        )

    async def handle_get_job_run(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        job_run_id = str(request.match_info["job_run_id"]).strip()
        if not job_run_id:
            return self._json_response({"error": "job_run_id_required"}, status=400)
        payload = self.store.get_job_run(job_run_id)
        if payload is None:
            return self._json_response({"error": "job_run_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_claim_dispatchable_job_run(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        job_run_id = str(request.match_info["job_run_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        started_at = str(payload.get("started_at") or datetime.now(timezone.utc).isoformat()).strip()
        try:
            claimed = self.store.claim_job_run(job_run_id, started_at)
        except ValueError as exc:
            status = 404 if str(exc) == "job_run_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(claimed)

    async def handle_retry_job_run(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        job_run_id = str(request.match_info["job_run_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        try:
            retried = self.store.retry_job_run(job_run_id, payload.get("scheduled_for"))
        except ValueError as exc:
            status = 404 if str(exc) in {"job_run_not_found", "schedule_not_found"} else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(retried, status=201)

    async def handle_execute_job(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        job_run_id = str(payload.get("job_run_id", "")).strip()
        job_type = str(payload.get("job_type", "")).strip()
        if not job_run_id:
            return self._json_response({"error": "job_run_id_required"}, status=400)
        if not job_type:
            return self._json_response({"error": "job_type_required"}, status=400)

        result_payload = {"job_type": job_type}
        if job_type == "telemetry_rollup":
            result_payload["aggregated_records"] = len(self.store.list_telemetry())
        elif job_type == "alarm_escalation":
            result_payload["open_alarm_count"] = len(self.store.list_alarms())
        elif job_type == "ota_campaign_tick":
            result_payload["campaign_count"] = len(self.store.list_ota_campaigns())

        try:
            completed = self.store.complete_job_run(
                job_run_id,
                {
                    "status": "completed",
                    "result": {
                        "status": "completed",
                        "executor_type": "platform",
                        "details": result_payload,
                    },
                },
            )
        except ValueError as exc:
            status = 404 if str(exc) == "job_run_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(completed)

    async def handle_complete_job_run(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        job_run_id = str(request.match_info["job_run_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            completed = self.store.complete_job_run(job_run_id, payload)
        except ValueError as exc:
            status = 404 if str(exc) == "job_run_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(completed)

    async def handle_fail_job_run(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        job_run_id = str(request.match_info["job_run_id"]).strip()
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)
        try:
            failed = self.store.fail_job_run(job_run_id, payload)
        except ValueError as exc:
            status = 404 if str(exc) == "job_run_not_found" else 400
            return self._json_response({"error": str(exc)}, status=status)
        return self._json_response(failed)

    async def handle_resolve_device_config(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        device_id = str(payload.get("device_id", "")).strip()
        client_id = payload.get("client_id")
        selected_module = payload.get("selected_module") or {}
        if not device_id:
            return self._json_response({"error": "device_id_required"}, status=400)

        try:
            resolved = self.store.resolve_device_config(
                self.config,
                device_id=device_id,
                client_id=client_id,
                selected_module=selected_module,
            )
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        except DeviceBindException as exc:
            return self._json_response(
                {"error": "device_bind_required", "bind_code": exc.bind_code},
                status=409,
            )

        resolved_config = resolved["resolved_config"]
        return self._json_response(
            {
                "device": resolved["device"],
                "binding": resolved.get("binding", {}),
                "agent": resolved["agent"],
                "plugins": resolved_config.get("plugins", {}),
                "context_providers": resolved_config.get("context_providers", []),
                "voiceprint": resolved_config.get("voiceprint", {}),
                "summaryMemory": resolved_config.get("summaryMemory", {}),
                "resolved_config": resolved_config,
            }
        )

    async def handle_get_runtime_binding_view(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        if not device_id:
            return self._json_response({"error": "device_id_required"}, status=400)
        try:
            payload = self.store.build_runtime_binding_view(device_id)
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_get_runtime_capability_routing_view(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        device_id = str(request.match_info["device_id"]).strip()
        if not device_id:
            return self._json_response({"error": "device_id_required"}, status=400)
        try:
            payload = self.store.build_runtime_capability_routing_view(device_id)
        except DeviceNotFoundException:
            return self._json_response({"error": "device_not_found"}, status=404)
        return self._json_response(payload)

    async def handle_report_chat_history(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            return self._json_response({"error": "invalid_json"}, status=400)

        session_id = str(payload.get("session_id", "")).strip()
        if not session_id:
            return self._json_response({"error": "session_id_required"}, status=400)
        record = self.store.append_chat_history(session_id, payload)
        return self._json_response(record, status=201)

    async def handle_generate_chat_summary(self, request: web.Request) -> web.Response:
        if not self._verify_control_secret(request):
            return self._json_response({"error": "control_secret_invalid"}, status=401)
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        summary_id = str(request.match_info["summary_id"]).strip()
        if not summary_id:
            return self._json_response({"error": "summary_id_required"}, status=400)
        record = self.store.save_summary_request(summary_id, payload)
        return self._json_response(record, status=202)
