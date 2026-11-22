import { createContext, useContext } from 'react'
import type { AnalyticsOverview } from '../types/analytics'

export interface AnalyticsContextValue {
  data: AnalyticsOverview | null
  loading: boolean
  error: string | null
  refresh: () => void
}

export const AnalyticsContext = createContext<AnalyticsContextValue | null>(null)

export function useAnalyticsOverview(): AnalyticsContextValue {
  const context = useContext(AnalyticsContext)
  if (!context) throw new Error('useAnalyticsOverview must be used within AnalyticsProvider')
  return context
}
