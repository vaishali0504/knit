import React, { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Mail,
  LayoutDashboard,
  Inbox,
  Briefcase,
  CalendarCheck,
  GraduationCap,
  Star,
  User,
  Tag,
  Bell,
  ShieldAlert,
  CheckSquare,
  Sparkles,
  BarChart3,
  Settings,
  LogOut,
  Search,
  Menu,
  X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Badge } from '../components/ui/Badge'
import { getEmailCounts } from '../services/emails'
import type { EmailCounts } from '../types/email'
import { getTaskCounts } from '../services/tasks'

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [emailCounts, setEmailCounts] = useState<EmailCounts | null>(null)
  const [pendingTaskCount, setPendingTaskCount] = useState<number | undefined>(undefined)

  useEffect(() => {
    let cancelled = false
    const refreshCounts = () => getEmailCounts()
      .then((counts) => {
        if (!cancelled) setEmailCounts(counts)
      })
      .catch(() => {
        if (!cancelled) setEmailCounts(null)
      })
    refreshCounts()
    const intervalId = window.setInterval(refreshCounts, 15000)
    window.addEventListener('knit:emails-changed', refreshCounts)
    return () => {
      cancelled = true
      window.clearInterval(intervalId)
      window.removeEventListener('knit:emails-changed', refreshCounts)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    getEmailCounts()
      .then((counts) => {
        if (!cancelled) setEmailCounts(counts)
      })
      .catch(() => {
        if (!cancelled) setEmailCounts(null)
      })
    return () => {
      cancelled = true
    }
  }, [location.pathname, location.search])

  useEffect(() => {
    let cancelled = false
    getTaskCounts()
      .then((counts) => {
        if (!cancelled) setPendingTaskCount(counts.pending + counts.in_progress || undefined)
      })
      .catch(() => {
        if (!cancelled) setPendingTaskCount(undefined)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/', { replace: true })
  }

  const navCategories = [
    { label: 'Overview', to: '/app', icon: LayoutDashboard, exact: true },
    { label: 'All Inbox', to: '/app/inbox', icon: Inbox },
    { label: 'Internship', to: '/app/inbox?category=internship', icon: Briefcase, badge: emailCounts?.internship },
    { label: 'Interview', to: '/app/inbox?category=interview', icon: CalendarCheck, badge: emailCounts?.interview },
    { label: 'College', to: '/app/inbox?category=college', icon: GraduationCap, badge: emailCounts?.college },
    { label: 'Important', to: '/app/inbox?category=important', icon: Star, badge: emailCounts?.important },
    { label: 'Personal', to: '/app/inbox?category=personal', icon: User, badge: emailCounts?.personal },
    { label: 'Promotions', to: '/app/inbox?category=promotions', icon: Tag, badge: emailCounts?.promotions },
    { label: 'Updates', to: '/app/inbox?category=updates', icon: Bell, badge: emailCounts?.updates },
    { label: 'Suspicious', to: '/app/inbox?category=suspicious', icon: ShieldAlert, badge: emailCounts?.suspicious },
    { label: 'Tasks', to: '/app/tasks', icon: CheckSquare, badge: pendingTaskCount },
    { label: 'AI Assistant', to: '/app/assistant', icon: Sparkles },
    { label: 'Analytics', to: '/app/analytics', icon: BarChart3 },
    { label: 'Settings', to: '/app/settings', icon: Settings },
  ]

  const isNavActive = (to: string, exact?: boolean) => {
    const currentPath = location.pathname + location.search
    if (exact) {
      return location.pathname === to && !location.search
    }
    if (to.includes('?')) {
      return currentPath === to
    }
    return location.pathname === to
  }

  const renderNavList = () => (
    <div className="flex flex-col space-y-1 py-2">
      {navCategories.map((item) => {
        const Icon = item.icon
        const active = isNavActive(item.to, item.exact)
        return (
          <NavLink
            key={item.label}
            to={item.to}
            onClick={() => setMobileSidebarOpen(false)}
            className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
              active
                ? 'bg-pink-surface text-coral font-bold shadow-xs'
                : 'text-foreground-secondary hover:text-foreground hover:bg-background-secondary'
            }`}
          >
            <div className="flex items-center gap-3">
              <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-coral' : 'text-foreground-secondary'}`} />
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  active ? 'bg-coral text-white' : 'bg-background-secondary border border-border text-foreground-secondary'
                }`}
              >
                {item.badge}
              </span>
            )}
          </NavLink>
        )
      })}
    </div>
  )

  return (
    <div className="min-h-screen bg-background-secondary flex flex-col lg:flex-row">
      {/* Desktop Left Sidebar (Sticky) */}
      <aside className="hidden lg:flex w-64 bg-white border-r border-border flex-col justify-between h-screen sticky top-0 z-30 select-none">
        <div className="flex flex-col h-full overflow-hidden">
          {/* Logo / Brand Header */}
          <div className="p-6 border-b border-border flex items-center justify-between">
            <NavLink to="/app" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-coral flex items-center justify-center text-white shadow-coral-sm">
                <Mail className="w-4.5 h-4.5" />
              </div>
              <div>
                <span className="font-extrabold text-xl tracking-tight text-foreground block leading-none">
                  KNIT
                </span>
                <span className="text-[10px] font-semibold text-coral uppercase tracking-wider block mt-1">
                  Workspace
                </span>
              </div>
            </NavLink>
            <Badge variant="pink" size="sm">
              MVP
            </Badge>
          </div>

          {/* 14 Navigation Items (Scrollable) */}
          <div className="flex-1 overflow-y-auto px-4 py-3 custom-scrollbar">
            <span className="text-[10px] font-bold uppercase tracking-wider text-foreground-secondary/70 px-3 block mb-1">
              Navigation
            </span>
            {renderNavList()}
          </div>

          {/* User Account Bar & Logout */}
          <div className="p-4 border-t border-border bg-background-secondary/40">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="w-8 h-8 rounded-lg bg-coral/10 text-coral font-bold text-xs flex items-center justify-center flex-shrink-0">
                  {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                  <span className="text-xs font-bold text-foreground block truncate">
                    {user?.full_name || 'User Account'}
                  </span>
                  <span className="text-[11px] text-foreground-secondary block truncate">
                    {user?.email}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="p-1.5 rounded-lg text-foreground-secondary hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Top Header */}
      <header className="lg:hidden bg-white border-b border-border sticky top-0 z-40 px-4 py-3 flex items-center justify-between">
        <NavLink to="/app" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-coral flex items-center justify-center text-white shadow-coral-sm">
            <Mail className="w-4 h-4" />
          </div>
          <span className="font-extrabold text-lg tracking-tight text-foreground">
            KNIT
          </span>
        </NavLink>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
            className="p-2 rounded-xl border border-border text-foreground-secondary hover:text-foreground"
            aria-label="Toggle navigation drawer"
          >
            {mobileSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Mobile Sidebar Overlay Drawer */}
      {mobileSidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-foreground/40 backdrop-blur-xs"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="relative w-72 max-w-[80%] bg-white h-full flex flex-col justify-between z-10 p-4 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-border">
              <span className="font-bold text-base text-foreground">Navigation Menu</span>
              <button
                onClick={() => setMobileSidebarOpen(false)}
                className="p-1 text-foreground-secondary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto py-2">
              {renderNavList()}
            </div>
            <div className="pt-4 border-t border-border flex items-center justify-between">
              <div className="text-xs">
                <span className="font-bold text-foreground block">{user?.email}</span>
                <span className="text-[10px] text-foreground-secondary">Authenticated</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-xs text-red-600 font-semibold p-2 flex items-center gap-1"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main App Workspace Canvas */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Utility Header */}
        <div className="hidden lg:flex bg-white border-b border-border h-16 px-8 items-center justify-between sticky top-0 z-20">
          {/* Global Search Bar */}
          <div className="relative w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground-secondary/70" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  const query = searchQuery.trim()
                  navigate(query ? `/app/inbox?q=${encodeURIComponent(query)}` : '/app/inbox')
                }
              }}
              placeholder="Search sample emails, tasks, or extracted opportunities..."
              className="w-full bg-background-secondary border border-border rounded-xl pl-10 pr-4 py-2 text-xs text-foreground placeholder:text-foreground-secondary/60 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral transition-all"
            />
          </div>

          {/* Quick Info & Navigation Status */}
          <div className="flex items-center gap-4 text-xs">
            <span className="text-foreground-secondary">
              Status: <span className="text-emerald-600 font-semibold">&bull; Active Session</span>
            </span>
            <NavLink
              to="/app/settings"
              className="text-foreground-secondary hover:text-coral transition-colors flex items-center gap-1 font-medium"
            >
              <Settings className="w-3.5 h-3.5" />
              Settings
            </NavLink>
          </div>
        </div>

        {/* Dynamic Nested Page Content */}
        <main className="flex-1 p-6 sm:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
