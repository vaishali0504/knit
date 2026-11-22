import { getToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export interface ConnectedAccount {
  id: number
  provider: 'gmail'
  email_address: string
  status: string
  scopes: string[]
  last_successful_sync_at: string | null
}

export interface SyncAccountResult {
  sync_type: 'initial' | 'incremental'
  status: string
  added: number
  updated: number
  removed: number
  last_successful_sync_at: string | null
  imported: number
  skipped: number
  failed: number
  limit_reached: boolean
  error_code: string | null
  message: string | null
}

export interface GmailConnectionStatus {
  enabled: boolean
  credentials_configured: boolean
  sync_max_messages: number
  sync_page_size: number
}

export class ConnectionApiError extends Error {
  readonly statusCode: number

  constructor(message: string, statusCode: number) {
    super(message)
    this.name = 'ConnectionApiError'
    this.statusCode = statusCode
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { Accept: 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers },
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    const detail = typeof payload.detail === 'string' ? payload.detail : `Connection request failed (${response.status})`
    throw new ConnectionApiError(detail, response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export async function listConnectedAccounts(): Promise<ConnectedAccount[]> {
  const result = await request<{ items: ConnectedAccount[] }>('/api/connections')
  return result.items
}

export function getGmailConnectionStatus(): Promise<GmailConnectionStatus> {
  return request<GmailConnectionStatus>('/api/connections/status')
}

export function updateGmailSyncSettings(
  syncMaxMessages: number,
  syncPageSize: number,
): Promise<GmailConnectionStatus> {
  return request<GmailConnectionStatus>('/api/connections/status', {
    method: 'PATCH',
    body: JSON.stringify({
      sync_max_messages: syncMaxMessages,
      sync_page_size: syncPageSize,
    }),
  })
}

export function startGmailAuthorization(): Promise<{ authorization_url: string }> {
  return request('/api/connections/gmail/authorize', { method: 'POST' })
}

export function disconnectAccount(id: number): Promise<void> {
  return request(`/api/connections/${id}`, { method: 'DELETE' })
}

export function syncAccount(id: number): Promise<SyncAccountResult> {
  return request(`/api/connections/${id}/sync`, { method: 'POST' })
}
