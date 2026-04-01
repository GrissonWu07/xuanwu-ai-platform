import { fireEvent, screen, waitFor, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

const jobsOverviewPayload = {
  summary: [
    { label: 'Healthy schedules', value: '18' },
    { label: 'Queued runs', value: '3' },
    { label: 'Success today', value: '21' },
  ],
  schedules: [
    {
      schedule_id: 'sched_telemetry_rollup',
      name: 'Telemetry rollup',
      executor_type: 'management',
      schedule: '0 * * * *',
      next_run_at: '2026-03-31T11:00:00+08:00',
      status: 'active',
    },
    {
      schedule_id: 'sched_alarm_sweep',
      name: 'Alarm sweep escalation',
      executor_type: 'management',
      schedule: '*/10 * * * *',
      next_run_at: '2026-03-31T10:40:00+08:00',
      status: 'queued',
    },
  ],
  runs: [
    {
      job_run_id: 'run_telemetry_1040',
      schedule_id: 'sched_telemetry_rollup',
      status: 'success',
      executor_type: 'management',
      started_at: '2026-03-31T10:40:00+08:00',
      finished_at: '2026-03-31T10:40:12+08:00',
    },
    {
      job_run_id: 'run_alarm_1030',
      schedule_id: 'sched_alarm_sweep',
      status: 'queued',
      executor_type: 'management',
      started_at: '2026-03-31T10:30:00+08:00',
      finished_at: '',
    },
  ],
}

const scheduleDetailPayload = {
  schedule_id: 'sched_alarm_sweep',
  name: 'Alarm sweep escalation',
  executor_type: 'management',
  schedule: '*/10 * * * *',
  timezone: 'Asia/Shanghai',
  next_run_at: '2026-03-31T10:40:00+08:00',
  status: 'queued',
  misfire_policy: 'run_once',
  misfire_grace_seconds: 120,
  retry_policy: 'fixed_backoff',
  max_retry_attempts: 2,
  retry_backoff_seconds: 30,
  payload: {
    site_id: 'site-sh-01',
    escalation_policy: 'warehouse-critical',
  },
}

const jobRunDetailPayload = {
  job_run_id: 'run_alarm_1030',
  schedule_id: 'sched_alarm_sweep',
  status: 'queued',
  executor_type: 'management',
  scheduled_for: '2026-03-31T10:30:00+08:00',
  started_at: '2026-03-31T10:30:00+08:00',
  finished_at: '',
  result: {
    status: 'pending',
    details: {
      site_id: 'site-sh-01',
      escalated_alarm_count: 0,
    },
  },
}

describe('JobsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders schedules and job detail using overview plus detail payloads', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => jobsOverviewPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep') {
        return Promise.resolve({
          ok: true,
          json: async () => scheduleDetailPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_1030') {
        return Promise.resolve({
          ok: true,
          json: async () => jobRunDetailPayload,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/jobs', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Jobs' })).toBeVisible()
    expect(await screen.findByRole('button', { name: /Telemetry rollup/i })).toBeVisible()
    expect(screen.getByText('Alarm sweep escalation')).toBeVisible()
    expect(screen.getByText('Healthy schedules')).toBeVisible()
    expect(screen.getByText('21')).toBeVisible()

    await fireEvent.click(screen.getByRole('button', { name: /Alarm sweep escalation/i }))

    const detail = await screen.findByTestId('job-detail-panel')
    expect(within(detail).getByText('queued')).toBeVisible()
    expect(within(detail).getByText('run_alarm_1030')).toBeVisible()
    expect(await within(detail).findByText('Asia/Shanghai')).toBeVisible()
    expect(await within(detail).findByText('site-sh-01')).toBeVisible()
    expect(await within(detail).findByText('warehouse-critical')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/jobs/overview', expect.any(Object))
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/jobs/schedules/sched_alarm_sweep', expect.any(Object))
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/jobs/runs/run_alarm_1030', expect.any(Object))
  })

  it('honors the scheduleId query parameter for initial selection', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => jobsOverviewPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep') {
        return Promise.resolve({
          ok: true,
          json: async () => scheduleDetailPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_1030') {
        return Promise.resolve({
          ok: true,
          json: async () => jobRunDetailPayload,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/jobs?scheduleId=sched_alarm_sweep', fetchMock)

    const detail = await screen.findByTestId('job-detail-panel')
    expect(await within(detail).findByText('Alarm sweep escalation')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/jobs/schedules/sched_alarm_sweep', expect.any(Object))
  })

  it('updates the route query when a different schedule is selected', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => jobsOverviewPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_telemetry_rollup') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            schedule_id: 'sched_telemetry_rollup',
            name: 'Telemetry rollup',
            executor_type: 'management',
            schedule: '0 * * * *',
            timezone: 'Asia/Shanghai',
            next_run_at: '2026-03-31T11:00:00+08:00',
            status: 'active',
            payload: {
              metric_family: 'telemetry',
            },
          }),
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_telemetry_1040') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            job_run_id: 'run_telemetry_1040',
            schedule_id: 'sched_telemetry_rollup',
            status: 'success',
            executor_type: 'management',
            scheduled_for: '2026-03-31T10:40:00+08:00',
            started_at: '2026-03-31T10:40:00+08:00',
            finished_at: '2026-03-31T10:40:12+08:00',
            result: {
              status: 'success',
              details: {
                metric_family: 'telemetry',
              },
            },
          }),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep') {
        return Promise.resolve({
          ok: true,
          json: async () => scheduleDetailPayload,
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_1030') {
        return Promise.resolve({
          ok: true,
          json: async () => jobRunDetailPayload,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    const { router } = await renderPortal('/jobs', fetchMock)

    await fireEvent.click(await screen.findByRole('button', { name: /Alarm sweep escalation/i }))

    await waitFor(() => {
      expect(router.currentRoute.value.query.scheduleId).toBe('sched_alarm_sweep')
    })
    const detail = await screen.findByTestId('job-detail-panel')
    expect(await within(detail).findByText('Alarm sweep escalation')).toBeVisible()
  })

  it('pauses, resumes, and manually triggers the selected schedule', async () => {
    const mutableOverview = structuredClone(jobsOverviewPayload)
    const mutableScheduleDetail = structuredClone(scheduleDetailPayload)
    const mutableJobRunDetail = structuredClone(jobRunDetailPayload)

    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone(mutableOverview),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep') {
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone(mutableScheduleDetail),
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_1030') {
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone(mutableJobRunDetail),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep:pause' && init?.method === 'POST') {
        mutableOverview.schedules[1].status = 'disabled'
        mutableScheduleDetail.status = 'disabled'
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone({ ...mutableScheduleDetail, enabled: false }),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep:resume' && init?.method === 'POST') {
        mutableOverview.schedules[1].status = 'active'
        mutableScheduleDetail.status = 'active'
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone({ ...mutableScheduleDetail, enabled: true }),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep:trigger' && init?.method === 'POST') {
        mutableOverview.runs.unshift({
          job_run_id: 'run_alarm_1040',
          schedule_id: 'sched_alarm_sweep',
          status: 'queued',
          executor_type: 'management',
          started_at: '2026-03-31T10:40:00+08:00',
          finished_at: '',
        })
        mutableJobRunDetail.job_run_id = 'run_alarm_1040'
        mutableJobRunDetail.scheduled_for = '2026-03-31T10:40:00+08:00'
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone({
            job_run_id: 'run_alarm_1040',
            schedule_id: 'sched_alarm_sweep',
            status: 'queued',
            executor_type: 'management',
            scheduled_for: '2026-03-31T10:40:00+08:00',
          }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/jobs?scheduleId=sched_alarm_sweep', fetchMock)

    const getDetailPanel = async () => screen.findByTestId('job-detail-panel')

    expect(await within(await getDetailPanel()).findByText('queued')).toBeVisible()

    await fireEvent.click(within(await getDetailPanel()).getByRole('button', { name: 'Pause schedule' }))
    expect(await within(await getDetailPanel()).findByText('disabled')).toBeVisible()

    await fireEvent.click(within(await getDetailPanel()).getByRole('button', { name: 'Resume schedule' }))
    expect(await within(await getDetailPanel()).findByText('active')).toBeVisible()

    await fireEvent.click(within(await getDetailPanel()).getByRole('button', { name: 'Run now' }))
    expect((await within(await getDetailPanel()).findAllByText('run_alarm_1040')).length).toBeGreaterThanOrEqual(1)

    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/jobs/schedules/sched_alarm_sweep:pause',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/jobs/schedules/sched_alarm_sweep:resume',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/jobs/schedules/sched_alarm_sweep:trigger',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('shows retry and misfire policies and retries the latest failed run', async () => {
    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            ...jobsOverviewPayload,
            runs: [
              {
                job_run_id: 'run_alarm_failed_1030',
                schedule_id: 'sched_alarm_sweep',
                status: 'failed',
                executor_type: 'management',
                started_at: '2026-03-31T10:30:00+08:00',
                finished_at: '2026-03-31T10:30:18+08:00',
              },
            ],
          }),
        })
      }

      if (input === '/control-plane/v1/jobs/schedules/sched_alarm_sweep') {
        return Promise.resolve({
          ok: true,
          json: async () => structuredClone(scheduleDetailPayload),
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_failed_1030') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            job_run_id: 'run_alarm_failed_1030',
            schedule_id: 'sched_alarm_sweep',
            status: 'failed',
            executor_type: 'management',
            scheduled_for: '2026-03-31T10:30:00+08:00',
            started_at: '2026-03-31T10:30:00+08:00',
            finished_at: '2026-03-31T10:30:18+08:00',
            error: {
              code: 'alarm_timeout',
              message: 'timeout',
            },
          }),
        })
      }

      if (input === '/control-plane/v1/jobs/runs/run_alarm_failed_1030:retry' && init?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            job_run_id: 'run_alarm_retry_1036',
            schedule_id: 'sched_alarm_sweep',
            status: 'queued',
            executor_type: 'management',
            scheduled_for: '2026-03-31T10:36:00+08:00',
            attempt: 2,
          }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/jobs?scheduleId=sched_alarm_sweep', fetchMock)

    const detail = await screen.findByTestId('job-detail-panel')
    expect(await within(detail).findByText('run_once')).toBeVisible()
    expect(await within(detail).findByText('120 seconds')).toBeVisible()
    expect(await within(detail).findByText('fixed_backoff')).toBeVisible()
    expect(await within(detail).findByText('2 attempts / 30s backoff')).toBeVisible()

    await fireEvent.click(within(detail).getByRole('button', { name: 'Retry failed run' }))

    expect(await within(detail).findByText('run_alarm_retry_1036')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/jobs/runs/run_alarm_failed_1030:retry',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
