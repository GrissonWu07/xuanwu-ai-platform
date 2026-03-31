import { afterEach, describe, expect, it, vi } from 'vitest'

describe('management api base url', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.resetModules()
    delete (window as Window & { __XUANWU_PORTAL_API_BASE_URL__?: string }).__XUANWU_PORTAL_API_BASE_URL__
  })

  it('prefixes requests with the runtime portal api base url when provided', async () => {
    ;(window as Window & { __XUANWU_PORTAL_API_BASE_URL__?: string }).__XUANWU_PORTAL_API_BASE_URL__ =
      'http://localhost:18082/'
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: 'owner-01', display_name: 'Owner', role_ids: [], permissions: [] }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { getAuthMe } = await import('@/api/management')
    await getAuthMe()

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:18082/control-plane/v1/auth/me',
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: 'application/json' }),
      }),
    )
  })
})
