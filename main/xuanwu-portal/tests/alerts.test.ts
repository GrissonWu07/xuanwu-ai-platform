import { fireEvent, screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

const alertsOverviewPayload = {
  summary: [
    { label: 'Active alerts', value: '2' },
    { label: 'Acknowledged', value: '4' },
    { label: 'Critical', value: '1' },
  ],
  alerts: [
    {
      alarm_id: 'alarm_gateway_latency',
      title: 'Gateway latency spike',
      severity: 'critical',
      status: 'active',
      source: 'gateway-west',
      created_at: '2026-03-31T10:24:00+08:00',
    },
  ],
  activity: [
    {
      id: 'activity_gateway_latency',
      title: 'Latency spike opened for gateway-west',
      detail: 'Operator was notified after the P95 latency crossed the red threshold.',
      at: '2026-03-31T10:25:00+08:00',
    },
  ],
}

const alarmsListPayload = {
  items: [
    alertsOverviewPayload.alerts[0],
    {
      alarm_id: 'alarm_assembly_panel',
      title: 'Assembly panel heartbeat lag',
      severity: 'medium',
      status: 'acknowledged',
      source: 'panel-07',
      created_at: '2026-03-31T09:54:00+08:00',
    },
  ],
}

const alarmDetailPayload = {
  alarm_id: 'alarm_gateway_latency',
  title: 'Gateway latency spike',
  severity: 'critical',
  status: 'active',
  source: 'gateway-west',
  created_at: '2026-03-31T10:24:00+08:00',
  message: 'Gateway west exceeded the latency budget for three consecutive intervals.',
  gateway_id: 'gw-west-01',
  device_id: 'dev-floor-02',
}

describe('AlertsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders alerts, hydrates alarm detail, and acknowledges the selected alarm', async () => {
    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/alerts/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => alertsOverviewPayload,
        })
      }

      if (input === '/control-plane/v1/alarms') {
        return Promise.resolve({
          ok: true,
          json: async () => alarmsListPayload,
        })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency') {
        return Promise.resolve({
          ok: true,
          json: async () => alarmDetailPayload,
        })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency:ack' && init?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ ok: true }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/alerts', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Alerts' })).toBeVisible()
    expect(await screen.findByRole('button', { name: /Gateway latency spike/i })).toBeVisible()
    expect(screen.getByText('Assembly panel heartbeat lag')).toBeVisible()

    const detail = await screen.findByTestId('alert-detail-panel')
    expect(within(detail).getByText('critical')).toBeVisible()
    expect(await within(detail).findByText('Gateway west exceeded the latency budget for three consecutive intervals.')).toBeVisible()
    expect(within(detail).getByText('gw-west-01')).toBeVisible()
    expect(within(detail).getByText('dev-floor-02')).toBeVisible()

    await fireEvent.click(within(detail).getByRole('button', { name: /Acknowledge alert/i }))

    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/alarms/alarm_gateway_latency', expect.any(Object))
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/alarms/alarm_gateway_latency:ack', expect.any(Object))
    expect(await within(detail).findByText('acknowledged')).toBeVisible()
  })

  it('honors the alarmId query parameter for initial selection', async () => {
    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/alerts/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => alertsOverviewPayload,
        })
      }

      if (input === '/control-plane/v1/alarms') {
        return Promise.resolve({
          ok: true,
          json: async () => alarmsListPayload,
        })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency') {
        return Promise.resolve({
          ok: true,
          json: async () => alarmDetailPayload,
        })
      }

      if (input === '/control-plane/v1/alarms/alarm_assembly_panel') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            ...alarmDetailPayload,
            alarm_id: 'alarm_assembly_panel',
            title: 'Assembly panel heartbeat lag',
            severity: 'medium',
            status: 'acknowledged',
            source: 'panel-07',
            gateway_id: 'gw-east-02',
            device_id: 'panel-07',
          }),
        })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency:ack' && init?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ ok: true }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/alerts?alarmId=alarm_assembly_panel', fetchMock)

    const detail = await screen.findByTestId('alert-detail-panel')
    expect(await within(detail).findByText('Assembly panel heartbeat lag')).toBeVisible()
    expect(await within(detail).findByText('gw-east-02')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/alarms/alarm_assembly_panel', expect.any(Object))
  })
})
