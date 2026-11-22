import { useEffect, useState } from 'react'
import { Check, Clipboard, LoaderCircle, Save, Sparkles } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { generateEmailReply, getReplyDraft, saveReplyDraft } from '../../services/replies'
import type { ReplyTone } from '../../types/reply'

interface ReplyComposerProps {
  emailId: number
  disabled?: boolean
}

const tones: { value: ReplyTone; label: string }[] = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'formal', label: 'Formal' },
  { value: 'short_direct', label: 'Short and Direct' },
]

export function ReplyComposer({ emailId, disabled = false }: ReplyComposerProps) {
  const [tone, setTone] = useState<ReplyTone>('professional')
  const [content, setContent] = useState('')
  const [loadingDraft, setLoadingDraft] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [copying, setCopying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    getReplyDraft(emailId)
      .then((draft) => {
        if (!cancelled && draft) {
          setContent(draft.content)
          setTone(draft.tone)
          setNotice('Saved draft loaded.')
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load the saved draft.')
      })
      .finally(() => {
        if (!cancelled) setLoadingDraft(false)
      })

    return () => {
      cancelled = true
    }
  }, [emailId])

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    setNotice(null)
    try {
      const result = await generateEmailReply(emailId, tone)
      setContent(result.reply_body)
      setNotice('Reply generated. Review and edit it before use.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate a reply.')
    } finally {
      setGenerating(false)
    }
  }

  const handleSave = async () => {
    if (!content.trim()) return
    setSaving(true)
    setError(null)
    setNotice(null)
    try {
      const draft = await saveReplyDraft(emailId, tone, content)
      setContent(draft.content)
      setNotice('Draft saved in KNIT.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save this draft.')
    } finally {
      setSaving(false)
    }
  }

  const handleCopy = async () => {
    if (!content.trim()) return
    setCopying(true)
    setError(null)
    setNotice(null)
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard access is unavailable in this browser context.')
      await navigator.clipboard.writeText(content)
      setNotice('Draft copied to clipboard.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to copy this draft.')
    } finally {
      setCopying(false)
    }
  }

  return (
    <section className="rounded-2xl border border-coral/20 bg-pink-surface/35 p-5 space-y-4" aria-labelledby="reply-composer-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-coral" aria-hidden="true" />
          <h2 id="reply-composer-title" className="text-base font-bold text-foreground">Contextual reply</h2>
        </div>
        <Badge variant="neutral" size="sm">Not sent</Badge>
      </div>

      <p className="text-xs leading-relaxed text-foreground-secondary">
        KNIT uses this email and any available analysis. Review the generated text carefully; it will not be sent.
      </p>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="flex-1 space-y-1.5 text-xs font-semibold text-foreground" htmlFor={`reply-tone-${emailId}`}>
          Reply tone
          <select
            id={`reply-tone-${emailId}`}
            value={tone}
            onChange={(event) => setTone(event.target.value as ReplyTone)}
            disabled={disabled || generating || loadingDraft}
            className="w-full rounded-xl border border-border bg-white px-3 py-2.5 text-sm font-normal text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral/40 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {tones.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <Button type="button" size="sm" onClick={handleGenerate} disabled={disabled || generating || loadingDraft}>
          {generating ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {generating ? 'Generating…' : 'Generate reply'}
        </Button>
      </div>

      <label className="block space-y-1.5 text-xs font-semibold text-foreground" htmlFor={`reply-content-${emailId}`}>
        Your reply draft
        <textarea
          id={`reply-content-${emailId}`}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          disabled={disabled || loadingDraft}
          maxLength={12000}
          rows={8}
          placeholder={loadingDraft ? 'Loading saved draft…' : 'Generate a reply or write your own draft.'}
          className="w-full resize-y rounded-xl border border-border bg-white px-3 py-3 text-sm font-normal leading-relaxed text-foreground placeholder:text-foreground-secondary/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral/40 disabled:cursor-not-allowed disabled:opacity-60"
        />
      </label>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-[11px] text-foreground-secondary">{content.length}/12000 characters</span>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" size="sm" onClick={handleCopy} disabled={disabled || !content.trim() || copying || loadingDraft}>
            {copying ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Clipboard className="h-4 w-4" />}
            {copying ? 'Copying…' : 'Copy draft'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={handleSave} disabled={disabled || !content.trim() || saving || loadingDraft}>
            {saving ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            {saving ? 'Saving…' : 'Save draft'}
          </Button>
        </div>
      </div>

      {(notice || error) && (
        <p className={`flex items-center gap-2 text-xs ${error ? 'text-red-600' : 'text-emerald-700'}`} role="status" aria-live="polite">
          {notice && <Check className="h-4 w-4 shrink-0" aria-hidden="true" />}
          {error || notice}
        </p>
      )}
    </section>
  )
}
