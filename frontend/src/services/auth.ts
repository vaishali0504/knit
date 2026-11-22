import type { LoginData, RegisterData, TokenResponse, User } from '../types/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const TOKEN_KEY = 'knit_auth_token'
const USER_KEY = 'knit_auth_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser(): User | null {
  const data = localStorage.getItem(USER_KEY)
  if (!data) return null
  try {
    return JSON.parse(data) as User
  } catch {
    return null
  }
}

export function setStoredUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeStoredUser(): void {
  localStorage.removeItem(USER_KEY)
}

export async function registerUser(data: RegisterData): Promise<TokenResponse> {
  const url = `${API_BASE_URL}/api/auth/register`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Registration failed (${res.status})`)
  }

  const result: TokenResponse = await res.json()
  setToken(result.access_token)
  setStoredUser(result.user)
  return result
}

export async function loginUser(data: LoginData): Promise<TokenResponse> {
  const url = `${API_BASE_URL}/api/auth/login`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Login failed (${res.status})`)
  }

  const result: TokenResponse = await res.json()
  setToken(result.access_token)
  setStoredUser(result.user)
  return result
}

export async function fetchCurrentUser(): Promise<User> {
  const token = getToken()
  if (!token) {
    throw new Error('No authentication token available')
  }

  const url = `${API_BASE_URL}/api/auth/me`
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!res.ok) {
    removeToken()
    removeStoredUser()
    throw new Error('Session expired or invalid')
  }

  const user: User = await res.json()
  setStoredUser(user)
  return user
}
