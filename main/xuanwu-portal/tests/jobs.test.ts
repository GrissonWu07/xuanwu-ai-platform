import { fireEvent, screen, within } from '@testing-library/vue'
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

describe('JobsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders schedules and run history using the jobs overview payload', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/jobs/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => jobsOverviewPayload,
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
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/jobs/overview', expect.any(Object))
  })
})
