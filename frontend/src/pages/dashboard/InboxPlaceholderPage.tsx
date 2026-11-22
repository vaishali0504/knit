import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  ArchiveRestore,
  ArrowLeft,
  Bell,
  Briefcase,
  CalendarCheck,
  ChevronLeft,
  ChevronRight,
  FileText,
  GraduationCap,
  Inbox,
  LoaderCircle,
  MailOpen,
  RefreshCw,
  Search,
  ShieldAlert,
  Star,
  Tag,
  Trash2,
  User,
  Sparkles,
  ShieldCheck,
  ExternalLink,
} from 'lucide-react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { ReplyComposer } from '../../components/email/ReplyComposer'
import {
  deleteEmail,
  getEmail,
  listEmails,
  permanentlyDeleteEmail,
  restoreEmail,
  setEmailImportant,
  setEmailRead,
  setEmailUnread,
  setEmailUnimportant,
} from '../../services/emails'
import type { EmailDetail, EmailListItem, EmailListResponse } from '../../types/email'
import type { AIAnalysisResponse, EmailCategory } from '../../types/ai'
import { analyzeEmail, correctEmailCategory, getEmailAnalysis } from '../../services/ai'

const categories = [
  { id: 'all', label: 'All Inbox', icon: Inbox },
  { id: 'internship', label: 'Internship', icon: Briefcase },
  { id: 'interview', label: 'Interview', icon: CalendarCheck },
  { id: 'college', label: 'College', icon: GraduationCap },
  { id: 'important', label: 'Important', icon: Star },
  { id: 'personal', label: 'Personal', icon: User },
  { id: 'promotions', label: 'Promotions', icon: Tag },
  { id: 'updates', label: 'Updates', icon: Bell },
  { id: 'suspicious', label: 'Suspicious', icon: ShieldAlert },
  { id: 'other', label: 'Other', icon: MailOpen },
]

function formatDate(value: string, includeTime = false): string {
  const date = new Date(value)
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: includeTime ? 'numeric' : undefined,
    hour: includeTime ? '2-digit' : undefined,
    minute: includeTime ? '2-digit' : undefined,
  }).format(date)
}

function senderInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || '?'
}

export const InboxPlaceholderPage: React.FC = () => {
  const navigate = useNavigate()
  const params = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const emailId = params.emailId ? Number(params.emailId) : null

  const activeCategory = searchParams.get('category') || 'all'
  const statusFilter = searchParams.get('status') as 'read' | 'unread' | null
  const searchInput = searchParams.get('q') || ''
  const sort = (searchParams.get('sort') || 'newest') as 'newest' | 'oldest'
  const deleted = searchParams.get('deleted') === 'true'
  const page = Math.max(1, Number(searchParams.get('page') || '1') || 1)

  const [search, setSearch] = useState(searchInput)
  const [data, setData] = useState<EmailListResponse | null>(null)
  const [detail, setDetail] = useState<EmailDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysisResponse | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await listEmails({
          category: activeCategory,
          status: statusFilter || undefined,
          search: searchInput || undefined,
          sort,
          page,
          pageSize: 20,
          deleted,
        })
        if (!cancelled) setData(result)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load emails.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    if (!emailId) load()
    return () => {
      cancelled = true
    }
  }, [activeCategory, statusFilter, searchInput, sort, page, deleted, emailId, refreshKey])

  useEffect(() => {
    let cancelled = false
    const loadDetail = async () => {
      if (!emailId) {
        setDetail(null)
        return
      }
      setDetailLoading(true)
      setError(null)
      try {
        const result = await getEmail(emailId)
        if (!cancelled) setDetail(result)
        try {
          const analysis = await getEmailAnalysis(emailId)
          if (!cancelled) {
            setAiAnalysis(analysis)
            setAiError(null)
          }
        } catch {
          if (!cancelled) setAiAnalysis(null)
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to open this email.')
      } finally {
        if (!cancelled) setDetailLoading(false)
      }
    }
    loadDetail()
    return () => {
      cancelled = true
    }
  }, [emailId])

  const updateParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    if (key !== 'page') next.delete('page')
    setSearchParams(next)
  }

  const submitSearch = (event: React.FormEvent) => {
    event.preventDefault()
    updateParam('q', search.trim() || null)
  }

  const openEmail = (email: EmailListItem) => {
    navigate(`/app/inbox/${email.id}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`)
  }

  const refreshDetail = async () => {
    if (!emailId) return
    setDetail(await getEmail(emailId))
  }

  const handleDelete = async (id: number) => {
    await deleteEmail(id)
    if (emailId) navigate(`/app/inbox?${searchParams.toString()}`)
    else {
      setData((current) => current ? { ...current, items: current.items.filter((item) => item.id !== id), total: current.total - 1 } : current)
    }
  }

  const handleAnalyze = async (regenerate = false) => {
    if (!emailId) return
    setAiLoading(true)
    setAiError(null)
    try {
      setAiAnalysis(await analyzeEmail(emailId, regenerate))
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Unable to analyze this email.')
    } finally {
      setAiLoading(false)
    }
  }

  const handleCategoryCorrection = async (category: EmailCategory) => {
    if (!emailId) return
    setAiLoading(true)
    setAiError(null)
    try {
      setAiAnalysis(await correctEmailCategory(emailId, category))
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Unable to save category correction.')
    } finally {
      setAiLoading(false)
    }
  }

  const activeTitle = useMemo(() => {
    if (deleted) return 'Trash'
    return categories.find((item) => item.id === activeCategory)?.label || 'All Inbox'
  }, [activeCategory, deleted])

  if (emailId) {
    return (
      <div className="space-y-5">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/app/inbox${searchParams.toString() ? `?${searchParams.toString()}` : ''}`)}
        >
          <ArrowLeft className="w-4 h-4" />
          Back to inbox
        </Button>

        {detailLoading ? (
          <div className="bg-white border border-border rounded-2xl p-12 flex justify-center">
            <LoaderCircle className="w-6 h-6 animate-spin text-coral" />
          </div>
        ) : error ? (
          <div className="bg-white border border-border rounded-2xl p-8 text-center space-y-3">
            <p className="text-sm text-red-600">{error}</p>
            <Button variant="secondary" size="sm" onClick={refreshDetail}>
              <RefreshCw className="w-4 h-4" />
              Retry
            </Button>
          </div>
        ) : detail ? (
          <article className="bg-white border border-border rounded-2xl overflow-hidden">
            <div className="px-5 sm:px-7 py-5 border-b border-border space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-2 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={detail.category === 'suspicious' ? 'warning' : 'pink'} size="md">
                      {detail.category}
                    </Badge>
                    {detail.is_important && <Star className="w-4 h-4 text-coral fill-coral" />}
                    <Badge variant="neutral" size="sm">Demo email</Badge>
                  </div>
                  <h1 className="text-xl sm:text-2xl font-bold text-foreground leading-snug">
                    {detail.subject}
                  </h1>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {detail.is_deleted ? (
                    <>
                      <Button variant="secondary" size="sm" onClick={async () => { await restoreEmail(detail.id); setDetail({ ...detail, is_deleted: false, deleted_at: null }); }}>
                        <ArchiveRestore className="w-4 h-4" />
                        Restore
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={async () => {
                          if (window.confirm('Permanently delete this demo email? This cannot be undone.')) {
                            await permanentlyDeleteEmail(detail.id)
                            navigate('/app/inbox?deleted=true')
                          }
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete permanently
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button variant="secondary" size="sm" onClick={async () => { const result = await (detail.is_read ? setEmailUnread(detail.id) : setEmailRead(detail.id)); setDetail({ ...detail, is_read: result.is_read }) }}>
                        <MailOpen className="w-4 h-4" />
                        {detail.is_read ? 'Mark unread' : 'Mark read'}
                      </Button>
                      <Button variant="secondary" size="sm" onClick={async () => { const result = await (detail.is_important ? setEmailUnimportant(detail.id) : setEmailImportant(detail.id)); setDetail({ ...detail, is_important: result.is_important }) }}>
                        <Star className={`w-4 h-4 ${detail.is_important ? 'fill-coral text-coral' : ''}`} />
                        {detail.is_important ? 'Remove important' : 'Mark important'}
                      </Button>
                      <Button variant="secondary" size="sm" onClick={() => handleDelete(detail.id)}>
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </Button>
                    </>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-pink-surface text-coral flex items-center justify-center font-bold flex-shrink-0">
                  {senderInitial(detail.sender_name)}
                </div>
                <div className="min-w-0 text-sm">
                  <p className="font-bold text-foreground">{detail.sender_name}</p>
                  <p className="text-xs text-foreground-secondary break-all">{detail.sender_email}</p>
                  <p className="text-xs text-foreground-secondary mt-1">To: {detail.recipient}</p>
                </div>
                <span className="ml-auto text-xs text-foreground-secondary whitespace-nowrap">
                  {formatDate(detail.received_at, true)}
                </span>
              </div>
            </div>

            <div className="px-5 sm:px-7 py-6 space-y-6">
              <section className="rounded-2xl border border-coral/20 bg-pink-surface/35 p-5 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-coral" />
                    <h2 className="text-base font-bold text-foreground">KNIT AI Intelligence</h2>
                    {aiAnalysis && <Badge variant="neutral" size="sm">Cached analysis</Badge>}
                  </div>
                  {detail.is_deleted ? null : (
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={aiLoading}
                      onClick={() => handleAnalyze(Boolean(aiAnalysis))}
                    >
                      {aiLoading ? <LoaderCircle className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                      {aiAnalysis ? 'Regenerate' : 'Analyze with AI'}
                    </Button>
                  )}
                </div>

                {aiLoading ? (
                  <div className="py-8 text-center text-sm text-foreground-secondary flex items-center justify-center gap-2">
                    <LoaderCircle className="w-5 h-5 animate-spin text-coral" />
                    Processing email securely...
                  </div>
                ) : aiError ? (
                  <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 space-y-3">
                    <p>{aiError}</p>
                    <Button variant="secondary" size="sm" onClick={() => handleAnalyze(Boolean(aiAnalysis))}>
                      <RefreshCw className="w-4 h-4" />
                      Retry
                    </Button>
                  </div>
                ) : aiAnalysis ? (
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    <div className="rounded-xl border border-border bg-white p-4 space-y-3">
                      <h3 className="text-sm font-bold text-foreground">AI Summary</h3>
                      <p className="text-sm font-medium text-foreground leading-relaxed">{aiAnalysis.summary}</p>
                      <div className="text-xs space-y-2">
                        <p><span className="font-bold text-foreground">Main purpose:</span> <span className="text-foreground-secondary">{aiAnalysis.main_purpose}</span></p>
                        {aiAnalysis.required_action && <p><span className="font-bold text-foreground">Required action:</span> <span className="text-foreground-secondary">{aiAnalysis.required_action}</span></p>}
                        {aiAnalysis.relevant_dates.length > 0 && (
                          <p><span className="font-bold text-foreground">Dates:</span> <span className="text-foreground-secondary">{aiAnalysis.relevant_dates.join(', ')}</span></p>
                        )}
                      </div>
                      {aiAnalysis.important_points.length > 0 && (
                        <ul className="list-disc pl-5 text-xs text-foreground-secondary space-y-1">
                          {aiAnalysis.important_points.map((point) => <li key={point}>{point}</li>)}
                        </ul>
                      )}
                    </div>

                    <div className="rounded-xl border border-border bg-white p-4 space-y-3">
                      <h3 className="text-sm font-bold text-foreground">Classification</h3>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="coral" size="md">{aiAnalysis.effective_category}</Badge>
                        <Badge variant="neutral" size="sm">{Math.round(aiAnalysis.category_confidence * 100)}% confidence</Badge>
                      </div>
                      <p className="text-xs text-foreground-secondary leading-relaxed">{aiAnalysis.category_explanation}</p>
                      {aiAnalysis.manual_category && (
                        <p className="text-[11px] text-coral font-semibold">Manually corrected; AI will not overwrite this category.</p>
                      )}
                      <label className="block text-xs font-semibold text-foreground">
                        Correct category
                        <select
                          value={aiAnalysis.manual_category || aiAnalysis.suggested_category}
                          onChange={(event) => handleCategoryCorrection(event.target.value as EmailCategory)}
                          className="mt-1.5 w-full bg-white border border-border rounded-xl px-3 py-2 text-xs text-foreground"
                        >
                          {['Internship','Interview','College','Important','Personal','Promotions','Updates','Suspicious','Other'].map((category) => (
                            <option key={category} value={category}>{category}</option>
                          ))}
                        </select>
                      </label>
                    </div>

                    <div className="rounded-xl border border-border bg-white p-4 space-y-3">
                      <h3 className="text-sm font-bold text-foreground">Extracted Information</h3>
                      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-xs">
                        {[
                          ['Organization', aiAnalysis.extracted.person_or_organization],
                          ['Company', aiAnalysis.extracted.company],
                          ['Role', aiAnalysis.extracted.role],
                          ['Stipend', aiAnalysis.extracted.stipend_or_compensation],
                          ['Application deadline', aiAnalysis.extracted.application_deadline],
                          ['Interview', aiAnalysis.extracted.interview_date_time],
                          ['Event date', aiAnalysis.extracted.event_date],
                          ['Event location', aiAnalysis.extracted.event_location],
                          ['Contact', aiAnalysis.extracted.contact_information],
                          ['Next action', aiAnalysis.extracted.next_action],
                        ].filter(([, value]) => value).map(([label, value]) => (
                          <div key={label as string}>
                            <dt className="font-bold text-foreground">{label}</dt>
                            <dd className="text-foreground-secondary break-words">{value}</dd>
                          </div>
                        ))}
                      </dl>
                      {aiAnalysis.extracted.application_or_registration_url && (
                        <a
                          href={aiAnalysis.extracted.application_or_registration_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-xs font-bold text-coral hover:text-coral-hover"
                        >
                          Open extracted link
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                      {aiAnalysis.extracted.skills.length > 0 && <p className="text-xs"><span className="font-bold">Skills:</span> {aiAnalysis.extracted.skills.join(', ')}</p>}
                      {aiAnalysis.extracted.eligibility.length > 0 && <p className="text-xs"><span className="font-bold">Eligibility:</span> {aiAnalysis.extracted.eligibility.join(', ')}</p>}
                      {aiAnalysis.extracted.required_documents.length > 0 && <p className="text-xs"><span className="font-bold">Documents:</span> {aiAnalysis.extracted.required_documents.join(', ')}</p>}
                    </div>

                    <div className="rounded-xl border border-border bg-white p-4 space-y-3">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-coral" />
                        <h3 className="text-sm font-bold text-foreground">Security Analysis</h3>
                        <Badge
                          variant={aiAnalysis.security_risk === 'High' ? 'warning' : aiAnalysis.security_risk === 'Medium' ? 'warning' : 'success'}
                          size="sm"
                          className="ml-auto"
                        >
                          {aiAnalysis.security_risk} risk
                        </Badge>
                      </div>
                      <p className="text-xs text-foreground-secondary leading-relaxed">{aiAnalysis.security_explanation}</p>
                      {aiAnalysis.security_warning_signs.length > 0 && (
                        <ul className="list-disc pl-5 text-xs text-foreground-secondary space-y-1">
                          {aiAnalysis.security_warning_signs.map((sign) => <li key={sign}>{sign}</li>)}
                        </ul>
                      )}
                      <p className="text-[11px] text-foreground-secondary">This is an AI assessment, not a guarantee that the email is safe or malicious.</p>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-xl border border-border bg-white p-5 text-center space-y-3">
                    <p className="text-sm text-foreground-secondary">Generate an AI analysis for this sample email when you are ready.</p>
                    <p className="text-xs text-foreground-secondary">No Gemini request is sent until you choose Analyze with AI.</p>
                  </div>
                )}
              </section>

              {detail.attachments.length > 0 && (
                <div className="border border-border rounded-xl p-4">
                  <p className="text-xs font-bold text-foreground mb-3">Demo attachments</p>
                  <div className="space-y-2">
                    {detail.attachments.map((attachment) => (
                      <div key={attachment.filename} className="flex items-center gap-3 rounded-lg bg-background-secondary px-3 py-2.5">
                        <FileText className="w-4 h-4 text-coral" />
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-foreground truncate">{attachment.name}</p>
                          <p className="text-[11px] text-foreground-secondary">{attachment.filename} · {attachment.size}</p>
                        </div>
                        <Badge variant="neutral" size="sm" className="ml-auto">Metadata only</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="text-sm text-foreground leading-7 whitespace-pre-wrap break-words">
                {detail.body}
              </div>
              {!detail.is_deleted && <ReplyComposer key={detail.id} emailId={detail.id} />}
            </div>
          </article>
        ) : null}
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">
              {activeTitle}
            </h1>
          </div>
        </div>
        <Button variant="secondary" size="sm" onClick={() => setRefreshKey((value) => value + 1)}>
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {categories.map((category) => {
          const Icon = category.icon
          const active = !deleted && activeCategory === category.id
          return (
            <button
              key={category.id}
              type="button"
              onClick={() => {
                const next = new URLSearchParams(searchParams)
                if (category.id === 'all') next.delete('category')
                else next.set('category', category.id)
                next.delete('deleted')
                next.delete('page')
                setSearchParams(next)
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-colors ${
                active
                  ? 'bg-coral text-white font-bold shadow-coral-sm'
                  : 'bg-white border border-border text-foreground-secondary hover:text-foreground hover:bg-background-secondary'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {category.label}
            </button>
          )
        })}
        <button
          type="button"
          onClick={() => {
            const next = new URLSearchParams()
            next.set('deleted', 'true')
            setSearchParams(next)
          }}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap ${
            deleted ? 'bg-coral text-white font-bold' : 'bg-white border border-border text-foreground-secondary'
          }`}
        >
          <Trash2 className="w-3.5 h-3.5" />
          Trash
        </button>
      </div>

      <div className="bg-white border border-border rounded-2xl p-3 flex flex-col md:flex-row gap-3">
        <form onSubmit={submitSearch} className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-secondary" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search sender, subject, or email content..."
            className="w-full bg-background-secondary border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm text-foreground placeholder:text-foreground-secondary/60 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral"
          />
        </form>
        <select
          value={statusFilter || 'all'}
          onChange={(event) => updateParam('status', event.target.value === 'all' ? null : event.target.value)}
          className="bg-white border border-border rounded-xl px-3 py-2.5 text-sm text-foreground"
        >
          <option value="all">All status</option>
          <option value="unread">Unread</option>
          <option value="read">Read</option>
        </select>
        <select
          value={sort}
          onChange={(event) => updateParam('sort', event.target.value)}
          className="bg-white border border-border rounded-xl px-3 py-2.5 text-sm text-foreground"
        >
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
        </select>
      </div>

      {loading ? (
        <div className="bg-white border border-border rounded-2xl p-12 flex justify-center">
          <LoaderCircle className="w-6 h-6 animate-spin text-coral" />
        </div>
      ) : error ? (
        <div className="bg-white border border-border rounded-2xl p-8 text-center space-y-3">
          <p className="text-sm text-red-600">{error}</p>
          <Button variant="secondary" size="sm" onClick={() => setRefreshKey((value) => value + 1)}>
            <RefreshCw className="w-4 h-4" />
            Retry
          </Button>
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="bg-white border border-border rounded-2xl overflow-hidden divide-y divide-border">
            {data.items.map((email) => (
              <button
                key={email.id}
                type="button"
                onClick={() => openEmail(email)}
                className={`w-full text-left px-4 sm:px-5 py-4 flex items-start gap-3 sm:gap-4 transition-colors ${
                  email.is_read ? 'bg-white hover:bg-background-secondary/60' : 'bg-pink-surface/35 hover:bg-pink-surface/60'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-pink-surface text-coral flex items-center justify-center font-bold flex-shrink-0">
                  {senderInitial(email.sender_name)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm truncate ${email.is_read ? 'font-medium text-foreground' : 'font-bold text-foreground'}`}>
                      {email.sender_name}
                    </span>
                    {email.is_important && <Star className="w-3.5 h-3.5 text-coral fill-coral flex-shrink-0" />}
                  </div>
                  <p className={`text-sm truncate mt-0.5 ${email.is_read ? 'text-foreground-secondary' : 'font-semibold text-foreground'}`}>
                    {email.subject}
                  </p>
                  <p className="text-xs text-foreground-secondary mt-1 line-clamp-1">
                    {email.preview}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={email.category === 'suspicious' ? 'warning' : 'neutral'} size="sm">
                      {email.category}
                    </Badge>
                    {email.attachment_count > 0 && (
                      <span className="text-[11px] text-foreground-secondary flex items-center gap-1">
                        <FileText className="w-3.5 h-3.5" />
                        {email.attachment_count}
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-xs text-foreground-secondary whitespace-nowrap">
                  {formatDate(email.received_at)}
                </span>
              </button>
            ))}
          </div>

          {data.total_pages > 1 && (
            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>{data.total} emails</span>
              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => updateParam('page', String(page - 1))}>
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>
                <span>Page {data.page} of {data.total_pages}</span>
                <Button variant="secondary" size="sm" disabled={page >= data.total_pages} onClick={() => updateParam('page', String(page + 1))}>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white border border-border rounded-2xl p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-xl bg-pink-surface text-coral flex items-center justify-center mx-auto">
            {deleted ? <Trash2 className="w-6 h-6" /> : <Inbox className="w-6 h-6" />}
          </div>
          <h2 className="text-base font-bold text-foreground">
            {deleted ? 'Trash is empty' : 'No emails match these filters'}
          </h2>
          <p className="text-sm text-foreground-secondary">
            {deleted ? 'Deleted sample emails can be restored or permanently removed.' : 'Try another category, status, or search term.'}
          </p>
        </div>
      )}
    </div>
  )
}
