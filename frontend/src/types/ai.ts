export type EmailCategory =
  | 'Internship'
  | 'Interview'
  | 'College'
  | 'Important'
  | 'Personal'
  | 'Promotions'
  | 'Updates'
  | 'Suspicious'
  | 'Other'

export interface ExtractedInformation {
  person_or_organization: string | null
  company: string | null
  role: string | null
  skills: string[]
  eligibility: string[]
  stipend_or_compensation: string | null
  application_deadline: string | null
  interview_date_time: string | null
  event_date: string | null
  event_location: string | null
  application_or_registration_url: string | null
  required_documents: string[]
  contact_information: string | null
  next_action: string | null
}

export interface AIAnalysisResponse {
  id: number
  email_id: number
  suggested_category: string
  category_confidence: number
  category_explanation: string
  manual_category: string | null
  effective_category: string
  summary: string
  main_purpose: string
  important_points: string[]
  required_action: string | null
  relevant_dates: string[]
  extracted: ExtractedInformation
  security_risk: 'Low' | 'Medium' | 'High'
  security_warning_signs: string[]
  security_explanation: string
  model_name: string
  prompt_version: string
  cached: boolean
  created_at: string
  updated_at: string
}
