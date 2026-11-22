import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { AnalyticsProvider } from './context/AnalyticsProvider'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardLayout } from './layouts/DashboardLayout'
import { DashboardOverviewPage } from './pages/dashboard/DashboardOverviewPage'
import { InboxPlaceholderPage } from './pages/dashboard/InboxPlaceholderPage'
import { TasksPlaceholderPage } from './pages/dashboard/TasksPlaceholderPage'
import { AssistantPlaceholderPage } from './pages/dashboard/AssistantPlaceholderPage'
import { SettingsPage } from './pages/dashboard/SettingsPage'

const AnalyticsPlaceholderPage = lazy(() =>
  import('./pages/dashboard/AnalyticsPlaceholderPage').then((module) => ({ default: module.AnalyticsPlaceholderPage })),
)

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Application Routes */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <AnalyticsProvider>
                  <DashboardLayout />
                </AnalyticsProvider>
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardOverviewPage />} />
            <Route path="inbox" element={<InboxPlaceholderPage />} />
            <Route path="inbox/:emailId" element={<InboxPlaceholderPage />} />
            <Route path="tasks" element={<TasksPlaceholderPage />} />
            <Route path="assistant" element={<AssistantPlaceholderPage />} />
            <Route path="analytics" element={<Suspense fallback={<div className="h-72 animate-pulse rounded-2xl border border-border bg-white" aria-label="Loading analytics page" />}><AnalyticsPlaceholderPage /></Suspense>} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Catch-all redirect to Landing Page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
