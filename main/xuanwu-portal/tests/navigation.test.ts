import { describe, expect, it } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/vue'
import { createRouter, createMemoryHistory } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'

async function renderApp(initialPath = '/overview') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  router.push(initialPath)

  render(App, {
    global: {
      plugins: [router],
    },
  })

  await router.isReady()
}

describe('portal navigation', () => {
  it('switches between the phase 1 workstreams from the top tabs', async () => {
    await renderApp('/overview')

    await fireEvent.click(screen.getByRole('tab', { name: 'Jobs' }))
    expect(await screen.findByRole('heading', { name: 'Jobs' })).toBeVisible()

    await fireEvent.click(screen.getByRole('tab', { name: 'Alerts' }))
    expect(await screen.findByRole('heading', { name: 'Alerts' })).toBeVisible()
  })

  it('opens the profile menu with secondary destinations', async () => {
    await renderApp('/overview')

    await fireEvent.click(screen.getByRole('button', { name: /profile menu/i }))

    expect(await screen.findByRole('menuitem', { name: 'Settings' })).toBeVisible()
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeVisible()
  })
})
