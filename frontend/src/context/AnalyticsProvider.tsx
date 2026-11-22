import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { AnalyticsContext } from './AnalyticsContext'
import { getAnalyticsOverview } from '../services/analytics'
import type { AnalyticsOverview } from '../types/analytics'

export function AnalyticsProvider({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()
  const shouldLoad = pathname === '/app' || pathname === '/app/analytics'
  const [data, setData] = useState<AnalyticsOverview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!shouldLoad) return
    let cancelled = false
    getAnalyticsOverview()
      .then((result) => {
        if (!cancelled) {
          setData(result)
          setError(null)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load analytics.')
      })
    return () => {
      cancelled = true
    }
  }, [shouldLoad, refreshKey])

  const refresh = useCallback(() => setRefreshKey((current) => current + 1), [])

  return (
    <AnalyticsContext.Provider value={{ data, loading: data === null && error === null, error, refresh }}>
      {children}
    </AnalyticsContext.Provider>
  )
}
