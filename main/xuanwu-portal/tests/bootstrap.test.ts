import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/vue'
import { createRouter, createMemoryHistory } from 'vue-router'

import App from '@/App.vue'
import { routes } from '@/router'

function renderApp(initialPath = '/overview') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  router.push(initialPath)

  return render(App, {
    global: {
      plugins: [router],
    },
  })
}

describe('portal bootstrap', () => {
  it('mounts the shell with the five primary tabs and no left sidebar', async () => {
    renderApp()

    expect(await screen.findByRole('tab', { name: 'Overview' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Devices' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Agents' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Jobs' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Alerts' })).toBeVisible()
    expect(screen.queryByTestId('left-sidebar')).not.toBeInTheDocument()
  })
})
