import { screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

describe('SettingsPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('supports query-backed selection for feature flags and service endpoints', async () => {
    const fetchMock = vi.fn((input: string) => {
      if (input === '/control-plane/v1/auth/me') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            user_id: 'user_gangwu',
            display_name: 'Gang Wu',
            email: 'gangwu@example.com',
            role_ids: ['platform_owner'],
            permissions: ['settings.read', 'users.read', 'devices.read'],
          }),
        })
      }

      if (input === '/control-plane/v1/portal/config') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            brand: { product_name: 'XuanWu Portal', support_email: 'support@example.com' },
            features: {
              jobs: true,
              alerts: true,
              telemetry: true,
            },
            endpoints: {
              management: 'http://management:8000',
              jobs: 'http://jobs:8010',
              gateway: 'http://gateway:8020',
            },
          }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/settings?featureId=alerts&endpointId=gateway', fetchMock)

    const featureDetail = await screen.findByTestId('feature-detail-panel')
    const endpointDetail = await screen.findByTestId('endpoint-detail-panel')

    expect(within(featureDetail).getByRole('heading', { name: 'alerts' })).toBeVisible()
    expect(within(featureDetail).getByText('Enabled')).toBeVisible()
    expect(within(endpointDetail).getByRole('heading', { name: 'gateway' })).toBeVisible()
    expect(within(endpointDetail).getByText('http://gateway:8020')).toBeVisible()
  })
})
