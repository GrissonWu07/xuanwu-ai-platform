import { fireEvent, render, screen, within } from '@testing-library/vue'
import { describe, expect, it } from 'vitest'
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
})
