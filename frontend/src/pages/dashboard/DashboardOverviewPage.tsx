import React from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  Briefcase,
  CalendarClock,
  CheckSquare,
  ChevronRight,
  Clock3,
  Inbox,
  Mail,
  RefreshCw,
  Sparkles,
  Star,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useAnalyticsOverview } from '../../context/AnalyticsContext'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(value))
}

function EmptyPanel({ children }: { children: React.ReactNode }) {
  return <div className="rounded-xl border border-dashed border-border bg-background-secondary px-4 py-6 text-center text-xs text-foreground-secondary">{children}</div>
}

export const DashboardOverviewPage: React.FC = () => {
  const { user } = useAuth()
  const { data, loading, error, refresh } = useAnalyticsOverview()
  const displayName = user?.full_name || user?.email?.split('@')[0] || 'User'

  if (!data && loading) {
    return (
      <div className="space-y-5" aria-label="Loading dashboard" aria-busy="true">
        <div className="h-16 animate-pulse rounded-2xl bg-pink-surface" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
          {Array.from({ length: 5 }, (_, index) => <div key={index} className="h-32 animate-pulse rounded-2xl border border-border bg-white" />)}
        </div>
        <div className="h-72 animate-pulse rounded-2xl border border-border bg-white" />
      </div>
    )
  }

  if (!data) {
    return (
      <Card className="p-8 text-center">
        <p className="text-sm font-semibold text-foreground">Dashboard data is unavailable.</p>
        <p className="mt-2 text-xs text-foreground-secondary">{error || 'Please try loading your analytics again.'}</p>
        <Button type="button" variant="secondary" size="sm" className="mt-4" onClick={refresh}>
          <RefreshCw className="h-4 w-4" /> Retry
        </Button>
      </Card>
    )
  }

  const openTasks = data.tasks.pending + data.tasks.in_progress
  const noRecords = data.emails.total === 0 && data.tasks.total === 0

  return (
    <div className="space-y-7 animate-in fade-in duration-300">
      <div className="flex flex-col justify-between gap-4 pb-1 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl">Welcome back, {displayName}</h1>
          <p className="mt-1 text-xs text-foreground-secondary sm:text-sm">Your inbox and task overview, based on your KNIT data.</p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Badge variant="neutral" size="sm">{data.timezone} dates</Badge>
          <Button type="button" variant="secondary" size="sm" onClick={refresh}>
            <RefreshCw className="h-4 w-4" /> Refresh
          </Button>
        </div>
      </div>

      {error && <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800" role="status">Refresh failed; showing the last loaded data. {error}</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Total emails" value={data.emails.total} hint="Active, non-deleted" icon={<Mail className="h-4 w-4" />} />
        <MetricCard label="Unread" value={data.emails.unread} hint="Needs your review" icon={<Inbox className="h-4 w-4" />} accent="text-coral" />
        <MetricCard label="Important" value={data.emails.important} hint="Flagged important" icon={<Star className="h-4 w-4" />} />
        <MetricCard label="Open tasks" value={openTasks} hint={`${data.tasks.pending} pending · ${data.tasks.in_progress} in progress`} icon={<CheckSquare className="h-4 w-4" />} />
        <MetricCard label="Due in 7 days" value={data.tasks.due_next_7_days} hint={`${data.tasks.overdue} overdue`} icon={<Clock3 className="h-4 w-4" />} accent={data.tasks.overdue ? 'text-amber-700' : undefined} />
      </div>

      {noRecords && (
        <Card className="p-5">
          <h2 className="text-sm font-bold text-foreground">No dashboard data yet</h2>
          <p className="mt-1 text-xs text-foreground-secondary">Emails and tasks you add to KNIT will appear here.</p>
          <Link to="/app/inbox" className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-coral hover:text-coral-hover">Open inbox <ArrowRight className="h-3.5 w-3.5" /></Link>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card className="p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-coral" />
            <h2 className="text-base font-bold text-foreground">Cached AI insight</h2>
          </div>
          {data.ai_insights.analysis_count === 0 ? (
            <EmptyPanel>No cached AI analysis is available yet. Analyze an email to see a data-based insight here.</EmptyPanel>
          ) : data.ai_insights.high_risk_flag_count > 0 ? (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-bold text-amber-900">{data.ai_insights.high_risk_flag_count} email(s) were flagged high risk by cached AI analysis.</p>
              <p className="mt-2 text-xs leading-relaxed text-amber-800">These are AI flags, not confirmed incidents. Review the original emails before acting.</p>
            </div>
          ) : (
            <div className="rounded-xl border border-border bg-background-secondary p-4 text-xs leading-relaxed text-foreground-secondary">
              Cached analysis is available for {data.ai_insights.analysis_count} email(s). No saved analysis currently flags an email as high risk; this is not a guarantee that messages are safe.
            </div>
          )}
        </Card>
        <Card className="flex flex-col justify-center p-5 sm:p-6">
          <div className="mb-3 flex items-center gap-2"><CalendarClock className="h-4 w-4 text-coral" /><h2 className="text-base font-bold text-foreground">30-day email activity</h2></div>
          <p className="text-3xl font-extrabold text-foreground">{data.email_activity.reduce((sum, day) => sum + day.count, 0)}</p>
          <p className="mt-1 text-xs text-foreground-secondary">Emails received from {formatDate(data.activity_start)} through {formatDate(data.activity_end)} ({data.timezone}).</p>
          <Link to="/app/analytics" className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-coral hover:text-coral-hover">Explore activity chart <ArrowRight className="h-3.5 w-3.5" /></Link>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-foreground">Upcoming deadlines</h2>
              <p className="mt-1 text-xs text-foreground-secondary">Nearest incomplete tasks with a due date.</p>
            </div>
            <Link to="/app/tasks" className="text-xs font-bold text-coral hover:text-coral-hover">View tasks</Link>
          </div>
          {data.upcoming_deadlines.length === 0 ? <EmptyPanel>No upcoming task deadlines.</EmptyPanel> : (
            <ul className="divide-y divide-border">
              {data.upcoming_deadlines.slice(0, 5).map((task) => (
                <li key={task.task_id} className="flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0">
                  <span className="min-w-0 text-sm font-semibold text-foreground">{task.title}<span className="mt-1 block text-xs font-normal text-foreground-secondary">{task.status.replace('_', ' ')} · {task.priority} priority</span></span>
                  <span className="shrink-0 text-xs font-semibold text-coral">{formatDate(task.due_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-foreground">Recent activity</h2>
              <p className="mt-1 text-xs text-foreground-secondary">Latest received emails and task updates.</p>
            </div>
            <Link to="/app/inbox" className="text-xs font-bold text-coral hover:text-coral-hover">Open inbox</Link>
          </div>
          {data.recent_activity.length === 0 ? <EmptyPanel>No recent email or task activity.</EmptyPanel> : (
            <ul className="divide-y divide-border">
              {data.recent_activity.slice(0, 6).map((item) => (
                <li key={`${item.type}-${item.id}`} className="py-3 first:pt-0 last:pb-0">
                  <Link to={item.email_id ? `/app/inbox/${item.email_id}` : '/app/tasks'} className="flex items-start justify-between gap-3 rounded-lg hover:bg-background-secondary/70">
                    <span className="flex min-w-0 items-start gap-2.5">
                      {item.type === 'email' ? <Mail className="mt-0.5 h-4 w-4 shrink-0 text-coral" /> : <CheckSquare className="mt-0.5 h-4 w-4 shrink-0 text-coral" />}
                      <span className="min-w-0"><span className="block truncate text-sm font-semibold text-foreground">{item.title}</span><span className="mt-0.5 block text-xs text-foreground-secondary">{item.detail}{item.category ? ` · ${item.category}` : ''}</span></span>
                    </span>
                    <time className="shrink-0 text-[11px] text-foreground-secondary" dateTime={item.timestamp}>{formatDate(item.timestamp)}</time>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <QuickLink to="/app/inbox" icon={<Briefcase className="h-4 w-4" />} title="Smart Inbox" detail="Browse your categorized email." />
        <QuickLink to="/app/tasks" icon={<CalendarClock className="h-4 w-4" />} title="Tasks & Deadlines" detail="Review and update your tasks." />
        <QuickLink to="/app/analytics" icon={<BarChart3 className="h-4 w-4" />} title="Email Analytics" detail="Explore your activity and trends." />
      </div>
    </div>
  )
}

function MetricCard({ label, value, hint, icon, accent }: { label: string; value: number; hint: string; icon: React.ReactNode; accent?: string }) {
  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-foreground-secondary">{label}</span>
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-pink-surface text-coral">{icon}</span>
      </div>
      <p className={`text-2xl font-extrabold ${accent || 'text-foreground'}`}>{value}</p>
      <p className="mt-1 text-[11px] text-foreground-secondary">{hint}</p>
    </Card>
  )
}

function QuickLink({ to, icon, title, detail }: { to: string; icon: React.ReactNode; title: string; detail: string }) {
  return (
    <Link to={to} className="group">
      <Card variant="interactive" className="flex h-full items-center gap-3 p-4">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-pink-surface text-coral">{icon}</span>
        <span className="min-w-0 flex-1"><span className="block text-sm font-bold text-foreground">{title}</span><span className="mt-0.5 block text-xs text-foreground-secondary">{detail}</span></span>
        <ChevronRight className="h-4 w-4 shrink-0 text-foreground-secondary transition-colors group-hover:text-coral" />
      </Card>
    </Link>
  )
}
