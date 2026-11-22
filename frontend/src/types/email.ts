export type EmailCategory =
  | 'internship'
  | 'interview'
  | 'college'
  | 'important'
  | 'personal'
  | 'promotions'
  | 'updates'
  | 'suspicious'
  | 'other'

export interface DemoAttachment {
  name: string
  filename: string
  size: string
  is_demo: boolean
}

export interface EmailListItem {
  id: number
  sender_name: string
  sender_email: string
  subject: string
  preview: string
  received_at: string
  category: EmailCategory
  is_read: boolean
  is_important: boolean
  is_deleted: boolean
  deleted_at: string | null
  attachment_count: number
}

export interface EmailDetail {
  id: number
  sender_name: string
  sender_email: string
  recipient: string
  subject: string
  body: string
  received_at: string
  category: EmailCategory
  is_read: boolean
  is_important: boolean
  is_deleted: boolean
  deleted_at: string | null
  attachments: DemoAttachment[]
}

export interface EmailListResponse {
  items: EmailListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface EmailCounts {
  all: number
  internship: number
  interview: number
  college: number
  important: number
  personal: number
  promotions: number
  updates: number
  suspicious: number
  other: number
  unread: number
  deleted: number
}

export interface EmailActionResponse {
  id: number
  is_read: boolean
  is_important: boolean
  is_deleted: boolean
  deleted_at: string | null
}
