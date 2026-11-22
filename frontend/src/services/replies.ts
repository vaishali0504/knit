import { getToken } from './auth'
import type { ReplyDraft, ReplyGenerationResponse, ReplyTone } from '../types/reply'

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
    throw new Error(error.detail || `Reply request failed (${response.status})`)
  }

  return response.json() as Promise<T>
}

export function generateEmailReply(emailId: number, tone: ReplyTone): Promise<ReplyGenerationResponse> {
  return request<ReplyGenerationResponse>(`/api/ai/emails/${emailId}/reply`, {
    method: 'POST',
    body: JSON.stringify({ tone }),
  })
}

export function getReplyDraft(emailId: number): Promise<ReplyDraft | null> {
  return request<ReplyDraft | null>(`/api/ai/emails/${emailId}/reply-draft`)
}

export function saveReplyDraft(
  emailId: number,
  tone: ReplyTone,
  content: string,
): Promise<ReplyDraft> {
  return request<ReplyDraft>(`/api/ai/emails/${emailId}/reply-draft`, {
    method: 'PUT',
    body: JSON.stringify({ tone, content }),
  })
}
