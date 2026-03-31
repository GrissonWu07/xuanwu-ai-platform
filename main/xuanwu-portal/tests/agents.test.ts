import { screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

const agentsPayload = {
  items: [
    {
      agent_id: 'agent_factory_ops',
      name: 'Factory operations copilot',
      status: 'active',
      provider_id: 'provider_openai_ops',
      model_id: 'model_gpt5_ops',
      updated_at: '2026-03-31T10:18:00+08:00',
    },
    {
      agent_id: 'agent_line_supervisor',
      name: 'Assembly line supervisor',
      status: 'degraded',
      provider_id: 'provider_local_fallback',
      model_id: 'model_local_fallback',
      updated_at: '2026-03-31T09:58:00+08:00',
    },
  ],
}

const providersPayload = {
  items: [
    {
      provider_id: 'provider_openai_ops',
      name: 'OpenAI operations',
      provider_type: 'openai',
      status: 'healthy',
      base_url: 'https://api.openai.example',
    },
  ],
}

const modelsPayload = {
  items: [
    {
      model_id: 'model_gpt5_ops',
      label: 'GPT-5 Ops',
      model_name: 'gpt-5',
      provider_id: 'provider_openai_ops',
      status: 'ready',
      capabilities: ['reasoning', 'tool_use'],
    },
  ],
}

describe('AgentsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders agent proxy data when the upstream proxy is available', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/xuanwu/agents') {
        return Promise.resolve({
          ok: true,
          json: async () => agentsPayload,
        })
      }

      if (input === '/control-plane/v1/xuanwu/model-providers') {
        return Promise.resolve({
          ok: true,
          json: async () => providersPayload,
        })
      }

      if (input === '/control-plane/v1/xuanwu/models') {
        return Promise.resolve({
          ok: true,
          json: async () => modelsPayload,
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/agents', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Agents' })).toBeVisible()
    expect(await screen.findByRole('button', { name: /Factory operations copilot/i })).toBeVisible()
    const detail = await screen.findByTestId('agent-detail-panel')
    expect(within(detail).getByText('OpenAI operations')).toBeVisible()
    expect(within(detail).getByText('GPT-5 Ops')).toBeVisible()
  })

  it('renders a graceful upstream-unavailable state instead of crashing', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/xuanwu/agents') {
        return Promise.resolve({
          ok: false,
          status: 502,
          json: async () => ({ message: 'upstream unavailable' }),
        })
      }

      if (input === '/control-plane/v1/xuanwu/model-providers' || input === '/control-plane/v1/xuanwu/models') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ items: [] }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/agents', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Agents' })).toBeVisible()
    expect(await screen.findByText('XuanWu upstream unavailable')).toBeVisible()
    expect(screen.getByText(/Agent proxy data is temporarily unavailable/i)).toBeVisible()
  })
})
