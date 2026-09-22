import type { FetchError, $fetch, type FetchOptions } from 'ofetch'

export const useApi = async <T>(url: string, options: FetchOptions<'json'> = {}): Promise<T> => {
  const config = useRuntimeConfig()
  const toast = useToast()

  const customFetch = $fetch.create({
    baseURL: config.public.apiBase,
    credentials: 'include'
  })

  try {
    return await customFetch<T>(url, options)
  } catch (e: unknown) {
    const error = e as FetchError<{ detail?: string }>
    const status = error.response?.status

    if (status === 401 && !url.includes('/api/v1/refresh')) {
      try {
        await customFetch('/api/v1/refresh', { method: 'POST' })

        return await customFetch<T>(url, options)
      } catch (refreshError) {
        if (import.meta.client) {
          navigateTo('/login')
        }
        throw refreshError
      }
    }

    const detail = error.response?._data?.detail || 'Произошла непредвиденная ошибка API'

    if (import.meta.client && status !== 401) {
      toast.add({
        title: `Ошибка ${status || ''}`,
        description: detail,
        color: 'error',
        icon: 'i-heroicons-exclamation-circle'
      })
    }

    throw error
  }
}
