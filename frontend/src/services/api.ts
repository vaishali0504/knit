import type { HealthResponse } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function checkBackendHealth(): Promise<HealthResponse> {
  const url = API_BASE_URL ? `${API_BASE_URL}/api/health` : '/api/health'
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Backend responded with status: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<HealthResponse>
}
