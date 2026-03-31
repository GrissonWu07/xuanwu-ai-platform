import { describe, expect, it, vi } from 'vitest'
import { fireEvent, screen, within } from '@testing-library/vue'

import { renderPortal } from './renderPortal'

function buildFetchMock() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input)
    if (path.endsWith('/control-plane/v1/auth/me')) {
      return new Response(
        JSON.stringify({
          user_id: 'user_gangwu',
          display_name: 'Gang Wu',
          email: 'gangwu@example.com',
          role_ids: ['platform_owner'],
          permissions: ['users.read', 'roles.read', 'devices.read', 'settings.read'],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/roles')) {
      return new Response(
        JSON.stringify({
          items: [
            {
              role_id: 'platform_owner',
              label: 'Platform owner',
              permission_count: 3,
              description: 'Owns the portal',
              permissions: ['users.read', 'roles.read', 'devices.read'],
            },
            {
              role_id: 'site_operator',
              label: 'Site operator',
              permission_count: 2,
              description: 'Operates the assigned site',
              permissions: ['devices.read', 'alerts.read'],
            },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/users')) {
      return new Response(
        JSON.stringify({
          items: [
            {
              user_id: 'user_gangwu',
              display_name: 'Gang Wu',
              email: 'gangwu@example.com',
              status: 'active',
              role_ids: ['platform_owner'],
            },
            {
              user_id: 'user_lin',
              display_name: 'Lin Chen',
              email: 'lin@example.com',
              status: 'invited',
              role_ids: ['site_operator'],
            },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/channels')) {
      return new Response(
        JSON.stringify({
          items: [
            {
              channel_id: 'channel_workshop',
              display_name: 'Workshop floor',
              owner_user_id: 'user_gangwu',
              status: 'active',
              device_count: 12,
            },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/gateways')) {
      return new Response(
        JSON.stringify({
          items: [
            {
              gateway_id: 'gateway_alpha',
              display_name: 'Gateway Alpha',
              adapter_type: 'mqtt',
              status: 'healthy',
              site_id: 'site_alpha',
            },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/channels/channel_workshop')) {
      return new Response(
        JSON.stringify({
          channel_id: 'channel_workshop',
          display_name: 'Workshop floor',
          owner_user_id: 'user_gangwu',
          status: 'active',
          device_count: 12,
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/gateways/gateway_alpha')) {
      return new Response(
        JSON.stringify({
          gateway_id: 'gateway_alpha',
          display_name: 'Gateway Alpha',
          adapter_type: 'mqtt',
          status: 'healthy',
          site_id: 'site_alpha',
          protocol_type: 'mqtt',
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/gateway/overview')) {
      return new Response(
        JSON.stringify({
          total_count: 1,
          protocol_distribution: { mqtt: 1 },
          site_distribution: { site_alpha: 1 },
          items: [
            {
              gateway_id: 'gateway_alpha',
              display_name: 'Gateway Alpha',
              protocol_type: 'mqtt',
              status: 'healthy',
              site_id: 'site_alpha',
            },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/xuanwu/agents')) {
      return new Response(
        JSON.stringify({
          items: [
            { agent_id: 'agent_ops', name: 'Ops Agent', status: 'active', provider_id: 'provider_openai', model_id: 'model_ops' },
            { agent_id: 'agent_line', name: 'Line Agent', status: 'draft', provider_id: 'provider_local', model_id: 'model_line' },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/xuanwu/model-providers')) {
      return new Response(
        JSON.stringify({
          items: [
            { provider_id: 'provider_openai', name: 'OpenAI', provider_type: 'openai', status: 'active' },
            { provider_id: 'provider_local', name: 'Local', provider_type: 'local', status: 'active' },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/xuanwu/models')) {
      return new Response(
        JSON.stringify({
          items: [
            { model_id: 'model_ops', label: 'Ops Model', model_name: 'gpt-5', provider_id: 'provider_openai', status: 'active' },
            { model_id: 'model_line', label: 'Line Model', model_name: 'qwen-max', provider_id: 'provider_local', status: 'draft' },
          ],
        }),
      )
    }
    if (path.endsWith('/control-plane/v1/portal/config')) {
      return new Response(
        JSON.stringify({
          brand: { product_name: 'XuanWu Portal', support_email: 'support@example.com' },
          features: { jobs: true, alerts: true },
          endpoints: { management: 'http://management:8000', jobs: 'http://jobs:8010' },
        }),
      )
    }
    throw new Error(`Unexpected request: ${path}`)
  })
}

describe('portal profile destinations', () => {
  it('renders users and roles with current profile, roles, and user directory data', async () => {
    const fetchMock = buildFetchMock()

    await renderPortal('/users-roles', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Users & Roles' })).toBeVisible()
    expect(
      await screen.findByText((content) => content.includes('Gang Wu currently holds') && content.includes('effective permissions.')),
    ).toBeVisible()
    expect((await screen.findAllByText('Platform owner')).length).toBeGreaterThan(0)
    expect((await screen.findAllByText('gangwu@example.com')).length).toBeGreaterThan(0)
  })

  it('renders channels, gateways, proxy data, and settings views with live management contracts', async () => {
    const fetchMock = buildFetchMock()

    await renderPortal('/channels-gateways?channelId=channel_workshop&gatewayId=gateway_alpha', fetchMock)
    expect(await screen.findByRole('heading', { name: 'Channels & Gateways' })).toBeVisible()
    expect(await screen.findByText('Protocol distribution')).toBeVisible()
    expect(await screen.findByText((content) => content.includes('mqtt') && content.includes('gateway'))).toBeVisible()
    const channelDetail = await screen.findByTestId('channel-detail-panel')
    const gatewayDetail = await screen.findByTestId('gateway-detail-panel')
    expect(within(channelDetail).getByRole('heading', { name: 'Workshop floor' })).toBeVisible()
    expect(within(channelDetail).getByText('user_gangwu')).toBeVisible()
    expect(within(gatewayDetail).getByRole('heading', { name: 'Gateway Alpha' })).toBeVisible()
    expect(within(gatewayDetail).getByText('site_alpha')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/gateway/overview', expect.any(Object))
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/channels/channel_workshop', expect.any(Object))
    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/gateways/gateway_alpha', expect.any(Object))

    await renderPortal('/ai-config-proxy', fetchMock)
    expect(await screen.findByRole('heading', { name: 'AI Config Proxy' })).toBeVisible()
    const agentDetail = await screen.findByTestId('agent-proxy-detail-panel')
    const providerDetail = await screen.findByTestId('provider-proxy-detail-panel')
    const modelDetail = await screen.findByTestId('model-proxy-detail-panel')
    expect(within(agentDetail).getByRole('heading', { name: 'Ops Agent' })).toBeVisible()
    expect(within(providerDetail).getByRole('heading', { name: 'OpenAI' })).toBeVisible()
    expect(within(modelDetail).getByRole('heading', { name: 'Ops Model' })).toBeVisible()

    await renderPortal('/settings', fetchMock)
    expect(await screen.findByRole('heading', { name: 'Settings' })).toBeVisible()
    expect(await screen.findByText('support@example.com')).toBeVisible()
    const endpointDetail = await screen.findByTestId('endpoint-detail-panel')
    expect(within(endpointDetail).getByRole('heading', { name: 'management' })).toBeVisible()
    expect(within(endpointDetail).getByText('http://management:8000')).toBeVisible()
  })

  it('honors query-backed detail selection for users/roles and AI proxy resources', async () => {
    const fetchMock = buildFetchMock()

    await renderPortal('/users-roles?userId=user_lin&roleId=site_operator', fetchMock)
    const userDetail = await screen.findByTestId('user-detail-panel')
    const roleDetail = await screen.findByTestId('role-detail-panel')
    expect(within(userDetail).getByRole('heading', { name: 'Lin Chen' })).toBeVisible()
    expect(within(userDetail).getByText('lin@example.com')).toBeVisible()
    expect(within(roleDetail).getByRole('heading', { name: 'Site operator' })).toBeVisible()
    expect(within(roleDetail).getByText('alerts.read')).toBeVisible()

    await renderPortal('/ai-config-proxy?agentId=agent_line&providerId=provider_local&modelId=model_line', fetchMock)
    const agentDetail = await screen.findByTestId('agent-proxy-detail-panel')
    const providerDetail = await screen.findByTestId('provider-proxy-detail-panel')
    const modelDetail = await screen.findByTestId('model-proxy-detail-panel')
    expect(within(agentDetail).getByRole('heading', { name: 'Line Agent' })).toBeVisible()
    expect(within(agentDetail).getByText('provider_local')).toBeVisible()
    expect(within(providerDetail).getByRole('heading', { name: 'Local' })).toBeVisible()
    expect(within(modelDetail).getByRole('heading', { name: 'Line Model' })).toBeVisible()
    expect(within(modelDetail).getByText('qwen-max')).toBeVisible()
  })

  it('updates the selected user status from the users and roles workspace', async () => {
    const mutableUsers = [
      {
        user_id: 'user_gangwu',
        display_name: 'Gang Wu',
        email: 'gangwu@example.com',
        status: 'active',
        role_ids: ['platform_owner'],
      },
      {
        user_id: 'user_lin',
        display_name: 'Lin Chen',
        email: 'lin@example.com',
        status: 'invited',
        role_ids: ['site_operator'],
      },
    ]

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input)
      if (path.endsWith('/control-plane/v1/auth/me')) {
        return new Response(
          JSON.stringify({
            user_id: 'user_gangwu',
            display_name: 'Gang Wu',
            email: 'gangwu@example.com',
            role_ids: ['platform_owner'],
            permissions: ['users.read', 'users.write', 'roles.read'],
          }),
        )
      }
      if (path.endsWith('/control-plane/v1/roles')) {
        return new Response(
          JSON.stringify({
            items: [
              {
                role_id: 'platform_owner',
                label: 'Platform owner',
                permission_count: 3,
                description: 'Owns the portal',
                permissions: ['users.read', 'roles.read', 'devices.read'],
              },
              {
                role_id: 'site_operator',
                label: 'Site operator',
                permission_count: 2,
                description: 'Operates the assigned site',
                permissions: ['devices.read', 'alerts.read'],
              },
            ],
          }),
        )
      }
      if (path.endsWith('/control-plane/v1/users')) {
        return new Response(JSON.stringify({ items: structuredClone(mutableUsers) }))
      }
      if (path.endsWith('/control-plane/v1/users/user_lin') && init?.method === 'PUT') {
        mutableUsers[1] = {
          ...mutableUsers[1],
          status: 'active',
        }
        return new Response(JSON.stringify(structuredClone(mutableUsers[1])))
      }
      throw new Error(`Unexpected request: ${path}`)
    })

    await renderPortal('/users-roles?userId=user_lin&roleId=site_operator', fetchMock)

    const userDetail = await screen.findByTestId('user-detail-panel')
    expect(within(userDetail).getByText('invited')).toBeVisible()

    await fireEvent.click(within(userDetail).getByRole('button', { name: 'Activate user' }))

    expect(await within(userDetail).findByText('active')).toBeVisible()
    expect(fetchMock).toHaveBeenCalledWith(
      '/control-plane/v1/users/user_lin',
      expect.objectContaining({ method: 'PUT' }),
    )
  })
})
