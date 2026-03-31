import { fireEvent, render, screen, waitFor, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'
import { renderPortal } from './renderPortal'

const devicesPayload = {
  items: [
    {
      device_id: 'edge-01',
      display_name: 'Workshop gateway alpha',
      owner_user_id: 'user_ops_north',
      lifecycle_status: 'active',
      bind_status: 'bound',
      device_type: 'gateway',
      protocol_type: 'mqtt',
      last_seen_at: '2026-03-31T10:32:00+08:00',
    },
    {
      device_id: 'panel-07',
      display_name: 'Assembly panel seven',
      owner_user_id: 'user_factory_ops',
      lifecycle_status: 'claimed',
      bind_status: 'pending',
      device_type: 'panel',
      protocol_type: 'websocket',
      last_seen_at: '2026-03-31T10:28:00+08:00',
    },
  ],
}

const firstDetail = {
  device: devicesPayload.items[0],
  binding: {
    agent_id: 'agent_factory_ops',
    channel_id: 'channel_workshop',
    model_config_id: 'model_gpt5_ops',
  },
  runtime: {
    session_status: 'healthy',
    capability_route_count: 6,
  },
  recent_events: [
    {
      id: 'evt_device_bound',
      title: 'Device bound to workshop channel',
      detail: 'edge-01 is serving workshop telemetry and command traffic.',
      at: '2026-03-31T10:20:00+08:00',
    },
  ],
  recent_telemetry: [
    {
      metric: 'temperature',
      value: '27.3 °C',
      at: '2026-03-31T10:31:00+08:00',
    },
  ],
}

const secondDetail = {
  device: devicesPayload.items[1],
  binding: {
    agent_id: 'agent_line_supervisor',
    channel_id: 'channel_assembly',
    model_config_id: 'model_local_fallback',
  },
  runtime: {
    session_status: 'pending_bind',
    capability_route_count: 2,
  },
  recent_events: [
    {
      id: 'evt_claim_requested',
      title: 'Claim request waiting for approval',
      detail: 'panel-07 is waiting for supervisory review before binding.',
      at: '2026-03-31T09:42:00+08:00',
    },
  ],
  recent_telemetry: [
    {
      metric: 'screen_brightness',
      value: '72%',
      at: '2026-03-31T10:27:00+08:00',
    },
  ],
}

async function renderDevicesWorkspace(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal('fetch', fetchMock)

  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })
  router.push('/devices')
  await router.isReady()

  return render(App, {
    global: {
      plugins: [router],
    },
  })
}

describe('DevicesPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders the collection and selected device detail with runtime binding context', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/devices') {
        return Promise.resolve({
          ok: true,
          json: async () => devicesPayload,
        })
      }

      if (input === '/control-plane/v1/devices/edge-01/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => firstDetail,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => secondDetail,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderDevicesWorkspace(fetchMock)

    expect(await screen.findByRole('heading', { name: 'Devices' })).toBeVisible()
    expect(await screen.findByRole('button', { name: /Workshop gateway alpha/i })).toBeVisible()
    expect(await screen.findByRole('button', { name: /Assembly panel seven/i })).toBeVisible()
    expect(await screen.findByText('agent_factory_ops')).toBeVisible()
    expect(screen.getByText('temperature')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/devices', expect.any(Object))

    const secondRow = screen.getByRole('button', { name: /Assembly panel seven/i })
    await fireEvent.click(secondRow)

    const detailPanel = await screen.findByTestId('device-detail-panel')
    expect(await within(detailPanel).findByText('agent_line_supervisor')).toBeVisible()
    expect(within(detailPanel).getByText('pending_bind')).toBeVisible()
    expect(within(detailPanel).getByText('screen_brightness')).toBeVisible()
  })

  it('honors the deviceId query parameter for initial selection', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/devices') {
        return Promise.resolve({
          ok: true,
          json: async () => devicesPayload,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => secondDetail,
        })
      }

      if (input === '/control-plane/v1/devices/edge-01/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => firstDetail,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/devices?deviceId=panel-07', fetchMock)

    const detailPanel = await screen.findByTestId('device-detail-panel')
    expect(await within(detailPanel).findByText('agent_line_supervisor')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/devices/panel-07/detail', expect.any(Object))
  })

  it('updates the route query when a different device is selected', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/devices') {
        return Promise.resolve({
          ok: true,
          json: async () => devicesPayload,
        })
      }

      if (input === '/control-plane/v1/devices/edge-01/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => firstDetail,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => secondDetail,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    const { router } = await renderPortal('/devices', fetchMock)

    await fireEvent.click(await screen.findByRole('button', { name: /Assembly panel seven/i }))

    await waitFor(() => {
      expect(router.currentRoute.value.query.deviceId).toBe('panel-07')
    })
    const detailPanel = await screen.findByTestId('device-detail-panel')
    expect(await within(detailPanel).findByText('agent_line_supervisor')).toBeVisible()
  })

  it('executes lifecycle actions against management APIs and refreshes device detail', async () => {
    const panelDetail = structuredClone(secondDetail)
    const panelDevice = structuredClone(devicesPayload.items[1])

    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/auth/me') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            user_id: 'user_gangwu',
            display_name: 'Gang Wu',
            role_ids: ['platform_owner'],
            permissions: ['devices.read', 'devices.write'],
          }),
        })
      }

      if (input === '/control-plane/v1/dashboard/overview') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            hero: {
              title: 'Overview',
              subtitle: 'Dashboard',
              primaryAction: 'Inspect devices',
              secondaryAction: 'Review alerts',
            },
            statusPills: [],
            quickStats: [
              { id: 'devices', label: 'Devices online', value: '2', delta: '+0' },
              { id: 'jobs', label: 'Jobs healthy', value: '2/2', delta: 'steady' },
              { id: 'proxy', label: 'Proxy sync', value: 'Live', delta: 'stable' },
            ],
            todaySummary: [],
            liveActivity: [],
          }),
        })
      }

      if (input === '/control-plane/v1/devices') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            items: [devicesPayload.items[0], panelDevice],
          }),
        })
      }

      if (input === '/control-plane/v1/devices/panel-07/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            ...panelDetail,
            device: panelDevice,
          }),
        })
      }

      if (input === '/control-plane/v1/devices/panel-07:claim' && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body))
        panelDevice.owner_user_id = payload.user_id
        panelDevice.lifecycle_status = 'claimed'
        panelDetail.device.owner_user_id = payload.user_id
        panelDetail.device.lifecycle_status = 'claimed'
        return Promise.resolve({
          ok: true,
          json: async () => panelDetail.device,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07:bind' && init?.method === 'POST') {
        panelDevice.bind_status = 'bound'
        panelDevice.lifecycle_status = 'bound'
        panelDetail.device.bind_status = 'bound'
        panelDetail.device.lifecycle_status = 'bound'
        return Promise.resolve({
          ok: true,
          json: async () => panelDetail.device,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07:suspend' && init?.method === 'POST') {
        panelDevice.lifecycle_status = 'suspended'
        panelDetail.device.lifecycle_status = 'suspended'
        return Promise.resolve({
          ok: true,
          json: async () => panelDetail.device,
        })
      }

      if (input === '/control-plane/v1/devices/panel-07:retire' && init?.method === 'POST') {
        panelDevice.lifecycle_status = 'retired'
        panelDetail.device.lifecycle_status = 'retired'
        return Promise.resolve({
          ok: true,
          json: async () => panelDetail.device,
        })
      }

      if (input === '/control-plane/v1/devices/edge-01/detail') {
        return Promise.resolve({
          ok: true,
          json: async () => firstDetail,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/devices?deviceId=panel-07', fetchMock)

    expect(within(await screen.findByTestId('device-detail-panel')).getByText('user_factory_ops')).toBeVisible()

    const getActionButton = async (name: string) => {
      const panel = await screen.findByTestId('device-detail-panel')
      return within(panel).getByRole('button', { name })
    }

    const expectDetailCardValue = async (label: string, value: string) => {
      const panel = await screen.findByTestId('device-detail-panel')
      const cardLabel = within(panel).getByText(label)
      const card = cardLabel.closest('.detail-card')
      expect(card).not.toBeNull()
      expect(within(card as HTMLElement).getByText(value)).toBeVisible()
    }

    await fireEvent.click(await getActionButton('Claim to me'))
    expect(await within(await screen.findByTestId('device-detail-panel')).findByText('user_gangwu')).toBeVisible()
    await waitFor(async () => {
      expect(await getActionButton('Bind device')).not.toBeDisabled()
    })

    await fireEvent.click(await getActionButton('Bind device'))
    await expectDetailCardValue('Binding', 'bound')
    await expectDetailCardValue('Lifecycle', 'bound')
    await waitFor(async () => {
      expect(await getActionButton('Suspend device')).not.toBeDisabled()
    })

    await fireEvent.click(await getActionButton('Suspend device'))
    await expectDetailCardValue('Lifecycle', 'suspended')
    await waitFor(async () => {
      expect(await getActionButton('Retire device')).not.toBeDisabled()
    })

    await fireEvent.click(await getActionButton('Retire device'))
    await expectDetailCardValue('Lifecycle', 'retired')

    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/devices/panel-07:claim',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/devices/panel-07:bind',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/devices/panel-07:suspend',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/devices/panel-07:retire',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
