export type ReplyTone = 'professional' | 'friendly' | 'formal' | 'short_direct'

export interface ReplyGenerationResponse {
  email_id: number
  tone: ReplyTone
  reply_body: string
}

export interface ReplyDraft {
  id: number
  email_id: number
  tone: ReplyTone
  content: string
  created_at: string
  updated_at: string
}
