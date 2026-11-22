import { getToken } from './auth'
import type { AnalyticsOverview } from '../types/analytics'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const token = getToken()
  const response = await fetch(`${API_BASE_URL}/api/analytics/overview`, {
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `Analytics request failed (${response.status})`)
  }

  return response.json() as Promise<AnalyticsOverview>
}
