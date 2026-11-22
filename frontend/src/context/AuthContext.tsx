import React, { createContext, useContext, useEffect, useState } from 'react'
import type { LoginData, RegisterData, User } from '../types/auth'
import {
  fetchCurrentUser,
  getStoredUser,
  getToken,
  loginUser,
  registerUser,
  removeStoredUser,
  removeToken,
} from '../services/auth'

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const [user, setUserState] = useState<User | null>(() => getStoredUser())
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const initializeAuth = async () => {
      const currentToken = getToken()
      if (currentToken) {
        try {
          const freshUser = await fetchCurrentUser()
          setUserState(freshUser)
          setTokenState(currentToken)
        } catch {
          setUserState(null)
          setTokenState(null)
        }
      } else {
        setUserState(null)
        setTokenState(null)
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const handleLogin = async (data: LoginData) => {
    setIsLoading(true)
    try {
      const result = await loginUser(data)
      setTokenState(result.access_token)
      setUserState(result.user)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (data: RegisterData) => {
    setIsLoading(true)
    try {
      const result = await registerUser(data)
      setTokenState(result.access_token)
      setUserState(result.user)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    removeToken()
    removeStoredUser()
    setTokenState(null)
    setUserState(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
