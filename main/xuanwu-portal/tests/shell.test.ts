import { fireEvent, render, screen, within } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'

async function renderShell() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  router.push('/overview')
  await router.isReady()

  return render(App, {
    global: {
      plugins: [router],
    },
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('portal shell', () => {
  it('renders centered primary tabs and an interactive profile menu without a sidebar', async () => {
    renderShell()

    const tabs = await screen.findByRole('tablist', { name: 'Primary navigation' })
    expect(within(tabs).getByRole('tab', { name: 'Overview' })).toBeVisible()
    expect(screen.queryByTestId('left-sidebar')).not.toBeInTheDocument()

    const profileTrigger = screen.getByRole('button', { name: /Gang Wu/i })
    expect(profileTrigger).toHaveAttribute('aria-expanded', 'false')

    await fireEvent.click(profileTrigger)

    expect(profileTrigger).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('menuitem', { name: 'Users & Roles' })).toBeVisible()
    expect(screen.getByRole('menuitem', { name: 'Settings' })).toBeVisible()
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeVisible()
  })

  it('hydrates the profile label and status cluster from management read models when available', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/control-plane/v1/auth/me')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            user_id: 'owner-01',
            display_name: 'Xuanwu Admin',
            role_ids: ['super-admin'],
            permissions: ['devices.read'],
          }),
        })
      }

      if (url.endsWith('/control-plane/v1/dashboard/overview')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            hero: {
              title: 'Fleet status',
              subtitle: 'Live',
              primaryAction: 'Open',
              secondaryAction: 'Review',
            },
            statusPills: [],
            quickStats: [
              { id: 'devices', label: 'Devices online', value: '248', delta: '+12' },
              { id: 'jobs', label: 'Active jobs', value: '12', delta: '+2' },
              { id: 'alerts', label: 'Open alerts', value: '3', delta: '-1' },
            ],
            todaySummary: [],
            liveActivity: [],
          }),
        })
      }

      return Promise.resolve({
        ok: false,
        json: async () => ({}),
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    renderShell()

    expect(await screen.findByRole('button', { name: /Xuanwu Admin profile menu/i })).toBeVisible()
    expect(await screen.findByText('super-admin')).toBeVisible()
    expect(await screen.findByText('248')).toBeVisible()
    expect(await screen.findByText('12')).toBeVisible()
  })
})
