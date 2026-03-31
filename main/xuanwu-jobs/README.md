# xuanwu-jobs

`xuanwu-jobs` is the platform job triggering service.

Current scope:

- poll due schedules from `xuanwu-management-server`
- enqueue jobs into Redis
- run local platform jobs with scalable worker replicas
- provide a dedicated scheduler service `xuanwu-jobs-scheduler`
- provide a horizontally scalable worker pool `xuanwu-jobs-platform-worker`

Current phase does not execute Agent jobs or gateway jobs locally in this repository.

## Docker scaling

Default Docker wiring runs:

- `redis`
- `xuanwu-jobs-scheduler`
- `xuanwu-jobs-platform-worker`

Increase platform throughput by scaling worker replicas:

```bash
docker compose up -d --scale xuanwu-jobs-platform-worker=3
```

This keeps one scheduler instance while allowing multiple `xuanwu-jobs-platform-worker` replicas to consume more platform jobs from Redis.
