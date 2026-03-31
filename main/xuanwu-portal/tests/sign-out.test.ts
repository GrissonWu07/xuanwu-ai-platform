import { fireEvent, screen } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderPortal } from './renderPortal'

describe('SignOutPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls the logout contract and confirms the signed-out state', async () => {
    const fetchMock = vi.fn((input: string, init?: RequestInit) => {
      if (input === '/control-plane/v1/auth/logout' && init?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({ ok: true }),
        })
      }

      throw new Error(`Unexpected request: ${input}`)
    })

    await renderPortal('/sign-out', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Sign out' })).toBeVisible()

    await fireEvent.click(screen.getByRole('button', { name: 'Sign out now' }))

    expect(fetchMock).toHaveBeenCalledWith('/control-plane/v1/auth/logout', expect.any(Object))
    expect(await screen.findByText('You have been signed out of the local control plane session.')).toBeVisible()
  })
})
