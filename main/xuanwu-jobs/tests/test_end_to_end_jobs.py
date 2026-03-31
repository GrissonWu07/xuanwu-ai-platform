import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile

from aiohttp import web


def _load_module(module_path: Path, module_name: str):
    service_root = module_path.parent if module_path.name == "app.py" else module_path.parents[1]
    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for name in list(sys.modules):
        if name == "config" or name.startswith("config."):
            sys.modules.pop(name, None)
        if name == "core" or name.startswith("core."):
            sys.modules.pop(name, None)
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scheduler_and_dispatcher_complete_due_job_through_management_api():
    async def scenario():
        root = Path(__file__).resolve().parents[3]
        management_app_module = _load_module(
            root / "main" / "xuanwu-management-server" / "app.py",
            "xuanwu_management_server_app_e2e",
        )
        scheduler_module = _load_module(
            root / "main" / "xuanwu-jobs" / "core" / "scheduler.py",
            "xuanwu_jobs_scheduler_e2e",
        )
        dispatcher_module = _load_module(
            root / "main" / "xuanwu-jobs" / "core" / "dispatcher.py",
            "xuanwu_jobs_dispatcher_e2e",
        )
        client_module = _load_module(
            root / "main" / "xuanwu-jobs" / "core" / "clients" / "management_client.py",
            "xuanwu_jobs_management_client_e2e",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "server": {"host": "127.0.0.1", "http_port": 18082, "auth_key": "runtime-secret"},
                "control-plane": {"data_dir": temp_dir, "secret": "runtime-secret"},
            }
            app = management_app_module.create_app(config)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)
            await site.start()
            port = site._server.sockets[0].getsockname()[1]

            store = app[management_app_module.CONTROL_PLANE_HANDLER_KEY].store
            schedule = store.save_schedule(
                "sched-telemetry-001",
                {
                    "schedule_id": "sched-telemetry-001",
                    "enabled": True,
                    "job_type": "telemetry_rollup",
                    "executor_type": "platform",
                    "interval_seconds": 300,
                    "next_run_at": "2026-03-31T10:00:00Z",
                    "payload": {"site_id": "site-a"},
                },
            )
            assert schedule["schedule_id"] == "sched-telemetry-001"

            jobs_config = {
                "management": {
                    "base_url": f"http://127.0.0.1:{port}",
                    "control_secret": "runtime-secret",
                },
                "jobs": {"schedule_batch_size": 10},
            }
            client = client_module.ManagementClient(jobs_config)
            dispatcher = dispatcher_module.JobDispatcher(
                management_client=client,
                gateway_client=None,
                device_client=None,
            )
            scheduler = scheduler_module.JobScheduler(client=client, dispatcher=dispatcher, config=jobs_config)

            await scheduler.run_once(now=scheduler_module.parse_timestamp("2026-03-31T10:00:00Z"))
            saved_runs = store.list_job_runs()
            await client.close()
            await runner.cleanup()

            assert len(saved_runs) == 1
            assert saved_runs[0]["status"] == "completed"
            assert saved_runs[0]["result"]["status"] == "completed"

    asyncio.run(scenario())
