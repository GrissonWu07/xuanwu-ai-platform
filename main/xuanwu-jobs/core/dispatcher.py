from __future__ import annotations


class JobDispatcher:
    def __init__(
        self,
        *,
        management_client,
        gateway_client,
        device_client,
        xuanwu_client=None,
    ):
        self.management_client = management_client
        self.gateway_client = gateway_client
        self.device_client = device_client
        self.xuanwu_client = xuanwu_client

    async def dispatch(self, job_message: dict) -> dict:
        executor_type = str(job_message.get("executor_type", "")).strip().lower()
        if executor_type in {"platform", "management"}:
            if self.management_client is None:
                return {"status": "failed", "error": "platform_executor_not_configured"}
            return await self.management_client.execute_job(job_message)
        if executor_type == "gateway":
            if self.gateway_client is None:
                return {"status": "failed", "error": "gateway_executor_not_configured"}
            return await self.gateway_client.execute_job(job_message)
        if executor_type == "device":
            if self.device_client is None:
                return {"status": "failed", "error": "device_executor_not_configured"}
            return await self.device_client.execute_job(job_message)
        if executor_type == "agent":
            if self.xuanwu_client is None:
                return {"status": "failed", "error": "agent_executor_not_configured"}
            return await self.xuanwu_client.execute_job(job_message)
        return {"status": "failed", "error": "unsupported_executor_type"}
