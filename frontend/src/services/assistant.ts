import { getToken } from './auth'
import type {
  AssistantConversation,
  AssistantConversationListResponse,
  AssistantMessage,
} from '../types/assistant'

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
    throw new Error(error.detail || `Assistant request failed (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function createConversation(title?: string): Promise<AssistantConversation> {
  return request<AssistantConversation>('/api/assistant/conversations', {
    method: 'POST',
    body: JSON.stringify({ title: title || null }),
  })
}

export function listConversations(
  page = 1,
  pageSize = 20,
): Promise<AssistantConversationListResponse> {
  return request<AssistantConversationListResponse>(
    `/api/assistant/conversations?page=${page}&pageSize=${pageSize}`,
  )
}

export function getConversation(id: number): Promise<AssistantConversation> {
  return request<AssistantConversation>(`/api/assistant/conversations/${id}`)
}

export function sendAssistantMessage(
  conversationId: number,
  content: string,
): Promise<AssistantMessage> {
  return request<AssistantMessage>(
    `/api/assistant/conversations/${conversationId}/messages`,
    { method: 'POST', body: JSON.stringify({ content }) },
  )
}

export function deleteConversation(id: number): Promise<void> {
  return request<void>(`/api/assistant/conversations/${id}`, { method: 'DELETE' })
}
