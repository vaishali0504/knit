export interface EmailSummaryMetrics {
  total: number
  unread: number
  important: number
}

export interface EmailCategoryMetric {
  category: string
  count: number
}

export interface EmailActivityDay {
  date: string
  count: number
}

export interface TaskSummaryMetrics {
  total: number
  pending: number
  in_progress: number
  completed: number
  overdue: number
  due_next_7_days: number
}

export interface UpcomingDeadline {
  task_id: number
  title: string
  due_at: string
  priority: string
  status: string
  source_email_id: number | null
}

export interface RecentActivityItem {
  type: 'email' | 'task'
  id: number
  title: string
  detail: string
  timestamp: string
  category: string | null
  status: string | null
  priority: string | null
  email_id: number | null
  task_id: number | null
}

export interface CachedAIInsights {
  analysis_count: number
  high_risk_flag_count: number
}

export interface AnalyticsOverview {
  timezone: 'UTC'
  activity_start: string
  activity_end: string
  emails: EmailSummaryMetrics
  email_categories: EmailCategoryMetric[]
  email_activity: EmailActivityDay[]
  tasks: TaskSummaryMetrics
  upcoming_deadlines: UpcomingDeadline[]
  recent_activity: RecentActivityItem[]
  ai_insights: CachedAIInsights
}
