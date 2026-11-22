export type TaskPriority = 'low' | 'medium' | 'high'
export type TaskStatus = 'pending' | 'in_progress' | 'completed'

export interface SourceEmail {
  id: number
  subject: string
  sender_name: string
}

export interface Task {
  id: number
  title: string
  description: string | null
  due_at: string | null
  priority: TaskPriority
  status: TaskStatus
  completed_at: string | null
  source_email_id: number | null
  source_email: SourceEmail | null
  created_at: string
  updated_at: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TaskCreateData {
  title: string
  description?: string | null
  due_at?: string | null
  priority: TaskPriority
  status: TaskStatus
  source_email_id?: number | null
}

export type TaskUpdateData = Partial<TaskCreateData>
