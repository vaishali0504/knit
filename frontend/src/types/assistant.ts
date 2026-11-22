export interface AssistantReference {
  email_id: number
  subject: string
  sender_name: string
  sender_email: string
}

export interface AssistantMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  references: AssistantReference[]
  created_at: string
}

export interface AssistantConversation {
  id: number
  title: string
  created_at: string
  updated_at: string
  messages: AssistantMessage[]
}

export interface AssistantConversationListItem {
  id: number
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface AssistantConversationListResponse {
  items: AssistantConversationListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
