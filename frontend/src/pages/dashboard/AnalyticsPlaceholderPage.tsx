import React from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, CheckSquare, Mail, RefreshCw, Sparkles } from 'lucide-react'
import { useAnalyticsOverview } from '../../context/AnalyticsContext'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { EmailActivityChart, EmailCategoryChart, TaskStatusChart } from '../../components/analytics/AnalyticsCharts'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(value))
}

function EmptyState({ text }: { text: string }) {
  return <div className="rounded-xl border border-dashed border-border bg-background-secondary px-4 py-6 text-center text-xs text-foreground-secondary">{text}</div>
}

export const AnalyticsPlaceholderPage: React.FC = () => {
  const { data, loading, error, refresh } = useAnalyticsOverview()

  if (!data && loading) {
    return (
      <div className="space-y-5" aria-label="Loading analytics" aria-busy="true">
        <div className="h-16 animate-pulse rounded-2xl bg-pink-surface" />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }, (_, index) => <div key={index} className="h-80 animate-pulse rounded-2xl border border-border bg-white" />)}
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <Card className="p-8 text-center">
        <p className="text-sm font-semibold text-foreground">Analytics are unavailable.</p>
        <p className="mt-2 text-xs text-foreground-secondary">{error || 'Please try loading your analytics again.'}</p>
        <Button type="button" variant="secondary" size="sm" className="mt-4" onClick={refresh}><RefreshCw className="h-4 w-4" /> Retry</Button>
      </Card>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl">Email Analytics</h1>
            <Badge variant="pink" size="sm">Your data</Badge>
          </div>
          <p className="mt-1 text-xs text-foreground-secondary sm:text-sm">
            Email activity from {formatDate(data.activity_start)} to {formatDate(data.activity_end)} ({data.timezone}).
          </p>
        </div>
        <Button type="button" variant="secondary" size="sm" onClick={refresh}><RefreshCw className="h-4 w-4" /> Refresh</Button>
      </div>

      {error && <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800" role="status">Refresh failed; showing the last loaded data. {error}</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={<Mail className="h-4 w-4" />} title="Active emails" value={data.emails.total} detail={`${data.emails.unread} unread`} />
        <SummaryCard icon={<span className="text-sm font-bold">★</span>} title="Important" value={data.emails.important} detail="Flagged important; separate from category" />
        <SummaryCard icon={<CheckSquare className="h-4 w-4" />} title="Open tasks" value={data.tasks.pending + data.tasks.in_progress} detail={`${data.tasks.pending} pending · ${data.tasks.in_progress} in progress`} />
        <SummaryCard icon={<BarChart3 className="h-4 w-4" />} title="Overdue tasks" value={data.tasks.overdue} detail={`${data.tasks.due_next_7_days} due in the next 7 days`} />
      </div>

      {data.emails.total === 0 && data.tasks.total === 0 && (
        <Card className="p-5">
          <h2 className="text-sm font-bold text-foreground">No analytics data yet</h2>
          <p className="mt-1 text-xs text-foreground-secondary">As emails and tasks are added to your KNIT account, charts and summaries will appear here.</p>
          <Link to="/app/inbox" className="mt-3 inline-flex text-xs font-bold text-coral hover:text-coral-hover">Open inbox</Link>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <EmailCategoryChart data={data.email_categories} />
        <TaskStatusChart data={data.tasks} />
      </div>
      <EmailActivityChart data={data.email_activity} />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card className="p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div><h2 className="text-base font-bold text-foreground">Upcoming deadlines</h2><p className="mt-1 text-xs text-foreground-secondary">Nearest incomplete tasks with due dates.</p></div>
            <Link to="/app/tasks" className="text-xs font-bold text-coral hover:text-coral-hover">View tasks</Link>
          </div>
          {data.upcoming_deadlines.length === 0 ? <EmptyState text="No upcoming deadlines are recorded." /> : (
            <ul className="divide-y divide-border">
              {data.upcoming_deadlines.map((task) => (
                <li key={task.task_id} className="flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0">
                  <span className="min-w-0 text-sm font-semibold text-foreground">{task.title}<span className="mt-1 block text-xs font-normal capitalize text-foreground-secondary">{task.status.replace('_', ' ')} · {task.priority} priority</span></span>
                  <time className="shrink-0 text-xs font-semibold text-coral" dateTime={task.due_at}>{formatDate(task.due_at)}</time>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-5 sm:p-6">
          <div className="mb-4"><h2 className="text-base font-bold text-foreground">Recent activity</h2><p className="mt-1 text-xs text-foreground-secondary">Email receipts and task updates from your account.</p></div>
          {data.recent_activity.length === 0 ? <EmptyState text="No recent email or task activity." /> : (
            <ul className="divide-y divide-border">
              {data.recent_activity.map((item) => (
                <li key={`${item.type}-${item.id}`} className="py-3 first:pt-0 last:pb-0">
                  <Link to={item.email_id ? `/app/inbox/${item.email_id}` : '/app/tasks'} className="flex items-start justify-between gap-3">
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

      <Card className="flex flex-col gap-3 p-5 sm:flex-row sm:items-start sm:p-6">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-pink-surface text-coral"><Sparkles className="h-4 w-4" /></span>
        <div>
          <h2 className="text-sm font-bold text-foreground">Cached AI insights</h2>
          {data.ai_insights.analysis_count === 0 ? (
            <p className="mt-1 text-xs leading-relaxed text-foreground-secondary">No saved email analyses are available, so AI insights are not shown. Generate an analysis from an email to populate this section. This dashboard does not request live AI analysis.</p>
          ) : data.ai_insights.high_risk_flag_count > 0 ? (
            <p className="mt-1 text-xs leading-relaxed text-foreground-secondary">Cached analysis has AI-flagged {data.ai_insights.high_risk_flag_count} email(s) as high risk out of {data.ai_insights.analysis_count} analyzed. These are assessments, not confirmed incidents; review the original messages.</p>
          ) : (
            <p className="mt-1 text-xs leading-relaxed text-foreground-secondary">{data.ai_insights.analysis_count} cached analyses are available; none currently flags an email as high risk. This is not a safety guarantee.</p>
          )}
        </div>
      </Card>
    </div>
  )
}

function SummaryCard({ icon, title, value, detail }: { icon: React.ReactNode; title: string; value: number; detail: string }) {
  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center justify-between gap-3"><span className="text-xs font-semibold uppercase tracking-wider text-foreground-secondary">{title}</span><span className="flex h-8 w-8 items-center justify-center rounded-lg bg-pink-surface text-coral">{icon}</span></div>
      <p className="text-2xl font-extrabold text-foreground">{value}</p>
      <p className="mt-1 text-[11px] text-foreground-secondary">{detail}</p>
    </Card>
  )
}
