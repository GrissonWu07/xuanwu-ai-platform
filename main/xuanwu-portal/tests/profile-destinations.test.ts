import { describe, expect, it, vi } from 'vitest'
import { screen } from '@testing-library/vue'

import { renderPortal } from './renderPortal'

describe('portal profile destinations', () => {
  it('renders users and roles with current profile, roles, and user directory data', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const path = String(input)
      if (path.endsWith('/control-plane/v1/auth/me')) {
        return new Response(
          JSON.stringify({
            user_id: 'user_gangwu',
            display_name: 'Gang Wu',
            email: 'gangwu@example.com',
            role_ids: ['platform_owner'],
            permissions: ['users.read', 'roles.read', 'devices.read'],
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
            ],
          }),
        )
      }
      throw new Error(`Unexpected request: ${path}`)
    })

    await renderPortal('/users-roles', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Users & Roles' })).toBeVisible()
    expect(
      await screen.findByText((content) => content.includes('Gang Wu currently holds') && content.includes('effective permissions.')),
    ).toBeVisible()
    expect((await screen.findAllByText('Platform owner')).length).toBeGreaterThan(0)
    expect((await screen.findAllByText('gangwu@example.com')).length).toBeGreaterThan(0)
  })

  it('renders channels, gateways, proxy data, and settings views with live management contracts', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const path = String(input)
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
      if (path.endsWith('/control-plane/v1/xuanwu/agents')) {
        return new Response(JSON.stringify({ items: [{ agent_id: 'agent_ops', name: 'Ops Agent', status: 'active' }] }))
      }
      if (path.endsWith('/control-plane/v1/xuanwu/model-providers')) {
        return new Response(
          JSON.stringify({
            items: [{ provider_id: 'provider_openai', name: 'OpenAI', provider_type: 'openai', status: 'active' }],
          }),
        )
      }
      if (path.endsWith('/control-plane/v1/xuanwu/models')) {
        return new Response(
          JSON.stringify({
            items: [{ model_id: 'model_ops', label: 'Ops Model', model_name: 'gpt-5', provider_id: 'provider_openai', status: 'active' }],
          }),
        )
      }
      if (path.endsWith('/control-plane/v1/auth/me')) {
        return new Response(
          JSON.stringify({
            user_id: 'user_gangwu',
            display_name: 'Gang Wu',
            email: 'gangwu@example.com',
            role_ids: ['platform_owner'],
            permissions: ['settings.read'],
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

    await renderPortal('/channels-gateways', fetchMock)
    expect(await screen.findByRole('heading', { name: 'Channels & Gateways' })).toBeVisible()
    expect(await screen.findByText('Workshop floor')).toBeVisible()
    expect(await screen.findByText('Gateway Alpha')).toBeVisible()

    await renderPortal('/ai-config-proxy', fetchMock)
    expect(await screen.findByRole('heading', { name: 'AI Config Proxy' })).toBeVisible()
    expect(await screen.findByText('Ops Agent')).toBeVisible()
    expect(await screen.findByText('OpenAI')).toBeVisible()
    expect(await screen.findByText('Ops Model')).toBeVisible()

    await renderPortal('/settings', fetchMock)
    expect(await screen.findByRole('heading', { name: 'Settings' })).toBeVisible()
    expect(await screen.findByText('support@example.com')).toBeVisible()
    expect(await screen.findByText('management')).toBeVisible()
    expect(await screen.findByText('http://management:8000')).toBeVisible()
  })
})
