import { cleanup, render } from '@testing-library/vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { vi } from 'vitest'

import App from '@/App.vue'
import { routes } from '@/router'

export async function renderPortal(initialPath: string, fetchMock?: ReturnType<typeof vi.fn>) {
  cleanup()

  if (fetchMock) {
    vi.stubGlobal('fetch', fetchMock)
  }

  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  router.push(initialPath)
  await router.isReady()

  const rendered = render(App, {
    global: {
      plugins: [router],
    },
  })

  return {
    router,
    ...rendered,
  }
}
