import { fireEvent, render, screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'

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
})
