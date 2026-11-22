import { getToken } from './auth'
import type { AIAnalysisResponse, EmailCategory } from '../types/ai'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `AI request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export function getEmailAnalysis(emailId: number): Promise<AIAnalysisResponse> {
  return request<AIAnalysisResponse>(`/api/ai/emails/${emailId}/analysis`)
}

export function analyzeEmail(emailId: number, regenerate = false): Promise<AIAnalysisResponse> {
  return request<AIAnalysisResponse>(
    `/api/ai/emails/${emailId}/analyze${regenerate ? '?regenerate=true' : ''}`,
    { method: 'POST' },
  )
}

export function correctEmailCategory(
  emailId: number,
  category: EmailCategory,
): Promise<AIAnalysisResponse> {
  return request<AIAnalysisResponse>(`/api/ai/emails/${emailId}/category`, {
    method: 'PATCH',
    body: JSON.stringify({ category }),
  })
}

export interface AIConnectionStatus {
  status: 'connected'
  model: string
  response: string
}

export function checkAIConnection(): Promise<AIConnectionStatus> {
  return request<AIConnectionStatus>('/api/ai/connection')
}
