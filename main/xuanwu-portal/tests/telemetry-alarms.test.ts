import { screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

const alertsOverviewPayload = {
  summary: [
    { label: 'Active alerts', value: '2' },
    { label: 'Acknowledged', value: '5' },
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

const telemetryPayload = {
  items: [
    {
      telemetry_id: 'tel_sensor_temp_001',
      device_id: 'dev-sensor-001',
      capability_code: 'sensor.temperature',
      value: '31.5',
      reported_at: '2026-03-31T10:31:00+08:00',
    },
    {
      telemetry_id: 'tel_switch_power_001',
      device_id: 'dev-switch-019',
      capability_code: 'switch.power',
      value: 'on',
      reported_at: '2026-03-31T10:30:00+08:00',
    },
  ],
}

const eventsPayload = {
  items: [
    {
      event_id: 'evt_gateway_latency_001',
      event_type: 'gateway.latency.spike',
      severity: 'warning',
      device_id: 'dev-gateway-west',
      gateway_id: 'gateway-west',
      occurred_at: '2026-03-31T10:25:00+08:00',
    },
    {
      event_id: 'evt_command_result_001',
      event_type: 'command.result',
      severity: 'info',
      device_id: 'dev-switch-019',
      gateway_id: 'gateway-west',
      occurred_at: '2026-03-31T10:29:00+08:00',
    },
  ],
}

const alarmsPayload = {
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

describe('TelemetryAlarmsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders telemetry, events, and alarms using live management contracts', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/alerts/overview') {
        return Promise.resolve({ ok: true, json: async () => alertsOverviewPayload })
      }

      if (input === '/control-plane/v1/telemetry') {
        return Promise.resolve({ ok: true, json: async () => telemetryPayload })
      }

      if (input === '/control-plane/v1/events') {
        return Promise.resolve({ ok: true, json: async () => eventsPayload })
      }

      if (input === '/control-plane/v1/alarms') {
        return Promise.resolve({ ok: true, json: async () => alarmsPayload })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            alarm_id: 'alarm_gateway_latency',
            title: 'Gateway latency spike',
            severity: 'critical',
            status: 'active',
            source: 'gateway-west',
            created_at: '2026-03-31T10:24:00+08:00',
            message: 'Operator was notified after the P95 latency crossed the red threshold.',
            gateway_id: 'gateway-west',
            device_id: 'dev-gateway-west',
          }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/telemetry-alarms', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Telemetry & Alarms' })).toBeVisible()
    const telemetryDetail = await screen.findByTestId('telemetry-detail-panel')
    const eventDetail = await screen.findByTestId('event-detail-panel')
    const alarmDetail = await screen.findByTestId('alarm-detail-panel')
    expect(within(telemetryDetail).getByRole('heading', { name: 'sensor.temperature' })).toBeVisible()
    expect(within(eventDetail).getByRole('heading', { name: 'gateway.latency.spike' })).toBeVisible()
    expect(within(alarmDetail).getByRole('heading', { name: 'Gateway latency spike' })).toBeVisible()
    expect(within(telemetryDetail).getByText('31.5')).toBeVisible()
  })

  it('supports query-backed telemetry, event, and alarm detail selection', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/alerts/overview') {
        return Promise.resolve({ ok: true, json: async () => alertsOverviewPayload })
      }

      if (input === '/control-plane/v1/telemetry') {
        return Promise.resolve({ ok: true, json: async () => telemetryPayload })
      }

      if (input === '/control-plane/v1/events') {
        return Promise.resolve({ ok: true, json: async () => eventsPayload })
      }

      if (input === '/control-plane/v1/alarms') {
        return Promise.resolve({ ok: true, json: async () => alarmsPayload })
      }

      if (input === '/control-plane/v1/alarms/alarm_gateway_latency') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            alarm_id: 'alarm_gateway_latency',
            title: 'Gateway latency spike',
            severity: 'critical',
            status: 'active',
            source: 'gateway-west',
            created_at: '2026-03-31T10:24:00+08:00',
            message: 'Operator was notified after the P95 latency crossed the red threshold.',
            gateway_id: 'gateway-west',
            device_id: 'dev-gateway-west',
          }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal(
      '/telemetry-alarms?telemetryId=tel_switch_power_001&eventId=evt_command_result_001&alarmId=alarm_gateway_latency',
      fetchMock,
    )

    const telemetryDetail = await screen.findByTestId('telemetry-detail-panel')
    const eventDetail = await screen.findByTestId('event-detail-panel')
    const alarmDetail = await screen.findByTestId('alarm-detail-panel')

    expect(within(telemetryDetail).getByRole('heading', { name: 'switch.power' })).toBeVisible()
    expect(within(telemetryDetail).getByText('dev-switch-019')).toBeVisible()
    expect(within(telemetryDetail).getByText('on')).toBeVisible()

    expect(within(eventDetail).getByRole('heading', { name: 'command.result' })).toBeVisible()
    expect(within(eventDetail).getByText('dev-switch-019')).toBeVisible()

    expect(within(alarmDetail).getByRole('heading', { name: 'Gateway latency spike' })).toBeVisible()
    expect(within(alarmDetail).getAllByText('gateway-west').length).toBeGreaterThan(0)
    expect(within(alarmDetail).getByText('Operator was notified after the P95 latency crossed the red threshold.')).toBeVisible()
  })
})
