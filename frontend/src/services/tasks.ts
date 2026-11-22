import { getToken } from './auth'
import type { Task, TaskListResponse, TaskCreateData, TaskUpdateData } from '../types/task'

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
    throw new Error(error.detail || `Task request failed (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export interface TaskQuery {
  status?: 'pending' | 'in_progress' | 'completed'
  priority?: 'low' | 'medium' | 'high'
  search?: string
  sort?: 'due' | 'oldest' | 'priority'
  page?: number
  pageSize?: number
}

export interface TaskCounts {
  all: number
  pending: number
  in_progress: number
  completed: number
  upcoming: number
}

export function getTaskCounts(): Promise<TaskCounts> {
  return request<TaskCounts>('/api/tasks/counts')
}

export function listTasks(query: TaskQuery = {}): Promise<TaskListResponse> {
  const params = new URLSearchParams()
  if (query.status) params.set('status', query.status)
  if (query.priority) params.set('priority', query.priority)
  if (query.search) params.set('search', query.search)
  params.set('sort', query.sort || 'due')
  params.set('page', String(query.page || 1))
  params.set('pageSize', String(query.pageSize || 20))
  return request<TaskListResponse>(`/api/tasks?${params.toString()}`)
}

export function getTask(id: number): Promise<Task> {
  return request<Task>(`/api/tasks/${id}`)
}

export function createTask(data: TaskCreateData): Promise<Task> {
  return request<Task>('/api/tasks', { method: 'POST', body: JSON.stringify(data) })
}

export function updateTask(id: number, data: TaskUpdateData): Promise<Task> {
  return request<Task>(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export function deleteTask(id: number): Promise<void> {
  return request<void>(`/api/tasks/${id}`, { method: 'DELETE' })
}
