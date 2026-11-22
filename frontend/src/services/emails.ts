import { getToken } from './auth'
import type {
  EmailActionResponse,
  EmailCounts,
  EmailDetail,
  EmailListResponse,
} from '../types/email'

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
    throw new Error(error.detail || `Request failed (${response.status})`)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export interface EmailQuery {
  category?: string
  status?: 'read' | 'unread'
  search?: string
  sort?: 'newest' | 'oldest'
  page?: number
  pageSize?: number
  deleted?: boolean
}

export function listEmails(query: EmailQuery = {}): Promise<EmailListResponse> {
  const params = new URLSearchParams()
  if (query.category && query.category !== 'all') params.set('category', query.category)
  if (query.status) params.set('status', query.status)
  if (query.search) params.set('search', query.search)
  params.set('sort', query.sort || 'newest')
  params.set('page', String(query.page || 1))
  params.set('pageSize', String(query.pageSize || 20))
  if (query.deleted) params.set('deleted', 'true')
  return request<EmailListResponse>(`/api/emails?${params.toString()}`)
}

export function getEmailCounts(): Promise<EmailCounts> {
  return request<EmailCounts>('/api/emails/counts')
}

export function getEmail(id: number): Promise<EmailDetail> {
  return request<EmailDetail>(`/api/emails/${id}`)
}

export function setEmailRead(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}/read`, { method: 'PATCH' })
}

export function setEmailUnread(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}/unread`, { method: 'PATCH' })
}

export function setEmailImportant(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}/important`, { method: 'PATCH' })
}

export function setEmailUnimportant(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}/unimportant`, { method: 'PATCH' })
}

export function deleteEmail(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}`, { method: 'DELETE' })
}

export function restoreEmail(id: number): Promise<EmailActionResponse> {
  return request<EmailActionResponse>(`/api/emails/${id}/restore`, { method: 'POST' })
}

export function permanentlyDeleteEmail(id: number): Promise<void> {
  return request<void>(`/api/emails/${id}/permanent`, { method: 'DELETE' })
}
