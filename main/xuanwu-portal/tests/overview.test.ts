import { render, screen, waitFor, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fireEvent } from '@testing-library/vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'

const dashboardPayload = {
  hero: {
    title: 'Unified operations for every device surface',
    subtitle:
      'Track ownership, active agents, schedules, and live alerts from one calm control center.',
    primaryAction: 'Review device activity',
    secondaryAction: 'Inspect job health',
  },
  statusPills: [
    { label: 'Healthy devices', value: '248' },
    { label: 'Agent links', value: '41' },
    { label: 'Pending jobs', value: '12' },
  ],
  quickStats: [
    { id: 'devices', label: 'Devices', value: '248', delta: '+14 this week' },
    { id: 'agents', label: 'Agents', value: '19', delta: '3 upstream offline' },
    { id: 'jobs', label: 'Jobs', value: '12', delta: '2 delayed' },
    { id: 'alerts', label: 'Alerts', value: '4', delta: '1 critical' },
  ],
  todaySummary: [
    { label: 'Claims processed', value: '18' },
    { label: 'Bindings updated', value: '6' },
    { label: 'Telemetry rollups', value: '1.2M' },
  ],
  liveActivity: [
    {
      id: 'evt_telemetry',
      title: 'Telemetry burst from floor-b gateway',
      detail: 'Gateway gw-factory-b forwarded 6,300 readings in the last 2 minutes.',
      at: '2026-03-31T11:04:00+08:00',
    },
    {
      id: 'evt_alert',
      title: 'Critical alert acknowledged',
      detail: 'Alert alarm_critical_press_21 was acknowledged by operator gang.wu.',
      at: '2026-03-31T10:58:00+08:00',
    },
  ],
}

const devicesPayload = {
  items: [
    {
      device_id: 'dev-lobby-01',
      display_name: 'Lobby panel',
      owner_user_id: 'user-gangwu',
      lifecycle_status: 'active',
      bind_status: 'bound',
      device_type: 'conversation',
      protocol_type: 'websocket',
      last_seen_at: '2026-03-31T11:08:00+08:00',
    },
  ],
}

const deviceDetailPayload = {
  device: devicesPayload.items[0],
  binding: {
    agent_id: 'agent-frontdesk',
    channel_id: 'channel-lobby',
    model_config_id: 'model-gpt-main',
  },
  runtime: {
    session_status: 'connected',
    capability_route_count: 4,
  },
  recent_events: [
    {
      id: 'evt-lobby-01',
      title: 'Lobby panel checked in',
      detail: 'Runtime heartbeat is healthy.',
      at: '2026-03-31T11:07:00+08:00',
    },
  ],
  recent_telemetry: [
    {
      metric: 'battery',
      value: '92%',
      at: '2026-03-31T11:06:00+08:00',
    },
  ],
}

describe('OverviewPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders the dashboard overview with quick stats and live activity', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => dashboardPayload,
    })
    vi.stubGlobal('fetch', fetchMock)

    const router = createRouter({
      history: createMemoryHistory(),
      routes,
    })
    router.push('/overview')
    await router.isReady()

    render(App, {
      global: {
        plugins: [router],
      },
    })

    expect(await screen.findByRole('heading', { name: dashboardPayload.hero.title })).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/dashboard/overview', expect.any(Object))

    const deviceCard = screen.getByTestId('quick-card-devices')
    expect(within(deviceCard).getByText('248')).toBeVisible()
    expect(within(deviceCard).getByText('+14 this week')).toBeVisible()

    expect(screen.getByText('Today Summary')).toBeVisible()
    expect(screen.getByText('Telemetry burst from floor-b gateway')).toBeVisible()

    await waitFor(() => {
      expect(screen.queryByText('Portal overview is loading.')).not.toBeInTheDocument()
    })
  })

  it('routes into the devices workspace from the devices quick card', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/dashboard/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => dashboardPayload,
        })
      }

      if (input === '/control-plane/v1/devices') {
        return Promise.resolve({
          ok: true,
          json: async () => devicesPayload,
        })
      }

      if (input === '/control-plane/v1/devices/dev-lobby-01/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => deviceDetailPayload,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    vi.stubGlobal('fetch', fetchMock)

    const router = createRouter({
      history: createMemoryHistory(),
      routes,
    })
    router.push('/overview')
    await router.isReady()

    render(App, {
      global: {
        plugins: [router],
      },
    })

    const deviceCard = await screen.findByTestId('quick-card-devices')
    await fireEvent.click(deviceCard)

    expect(await screen.findByRole('heading', { name: 'Devices' })).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/devices', expect.any(Object))
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/devices/dev-lobby-01/detail', expect.any(Object))
    })
  })
})
