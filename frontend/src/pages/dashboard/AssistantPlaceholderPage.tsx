import React, { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useNavigate } from 'react-router-dom'
import {
  ChevronLeft,
  ChevronRight,
  LoaderCircle,
  MessageSquare,
  Plus,
  RefreshCw,
  Send,
  Sparkles,
  Trash2,
} from 'lucide-react'
import { Button } from '../../components/ui/Button'
import {
  createConversation,
  deleteConversation,
  getConversation,
  listConversations,
  sendAssistantMessage,
} from '../../services/assistant'
import type {
  AssistantConversation,
  AssistantConversationListItem,
} from '../../types/assistant'

const suggestions = [
  'Which emails contain upcoming deadlines?',
  'Summarize my latest interview invitations.',
  'Find my internship opportunities.',
  'What important emails need my attention?',
]

export const AssistantPlaceholderPage: React.FC = () => {
  const navigate = useNavigate()
  const bottomRef = useRef<HTMLDivElement>(null)
  const [conversationItems, setConversationItems] = useState<AssistantConversationListItem[]>([])
  const [conversation, setConversation] = useState<AssistantConversation | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loadingList, setLoadingList] = useState(true)
  const [loadingConversation, setLoadingConversation] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [retryPrompt, setRetryPrompt] = useState<string | null>(null)

  const loadList = async (nextPage = page) => {
    setLoadingList(true)
    setError(null)
    try {
      const result = await listConversations(nextPage, 20)
      setConversationItems(result.items)
      setPage(result.page)
      setTotalPages(result.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load conversations.')
    } finally {
      setLoadingList(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    listConversations(1, 20)
      .then((result) => {
        if (!cancelled) {
          setConversationItems(result.items)
          setPage(result.page)
          setTotalPages(result.total_pages)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load conversations.')
      })
      .finally(() => {
        if (!cancelled) setLoadingList(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages.length])

  const startConversation = async (title?: string) => {
    setLoadingConversation(true)
    setError(null)
    try {
      const result = await createConversation(title)
      setConversation(result)
      await loadList(1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create conversation.')
    } finally {
      setLoadingConversation(false)
    }
  }

  const openConversation = async (id: number) => {
    setLoadingConversation(true)
    setError(null)
    try {
      setConversation(await getConversation(id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to open conversation.')
    } finally {
      setLoadingConversation(false)
    }
  }

  const submitMessage = async (event: React.FormEvent) => {
    event.preventDefault()
    await sendContent(message)
  }

  const sendContent = async (contentValue: string) => {
    const content = contentValue.trim()
    if (!content || sending) return

    setSending(true)
    setError(null)
    setRetryPrompt(null)
    setMessage('')

    try {
      let active = conversation
      if (!active) {
        active = await createConversation(content.slice(0, 80))
      }
      const optimisticMessage = {
        id: -Date.now(),
        role: 'user' as const,
        content,
        references: [],
        created_at: new Date().toISOString(),
      }
      setConversation({
        ...active,
        messages: [...active.messages, optimisticMessage],
      })

      await sendAssistantMessage(active.id, content)
      setConversation(await getConversation(active.id))
      await loadList(1)
    } catch (err) {
      setRetryPrompt(content)
      setError(err instanceof Error ? err.message : 'Unable to send your question.')
      setConversation((current) =>
        current
          ? { ...current, messages: current.messages.filter((item) => item.id >= 0) }
          : current,
      )
    } finally {
      setSending(false)
    }
  }

  const removeConversation = async (id: number) => {
    if (!window.confirm('Delete this assistant conversation?')) return
    try {
      await deleteConversation(id)
      if (conversation?.id === id) setConversation(null)
      await loadList(page)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to delete conversation.')
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[260px_minmax(0,1fr)] gap-5 min-h-[600px]">
      <aside className="bg-white border border-border rounded-2xl p-3 xl:h-[calc(100vh-160px)] xl:sticky xl:top-20 flex flex-col">
        <div className="flex items-center justify-between px-1 pb-3">
          <h1 className="text-sm font-bold text-foreground">Conversations</h1>
          <button
            type="button"
            onClick={() => startConversation()}
            className="p-2 rounded-lg border border-border text-coral hover:bg-pink-surface"
            title="New conversation"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {loadingList ? (
          <div className="flex-1 flex items-center justify-center">
            <LoaderCircle className="w-5 h-5 animate-spin text-coral" />
          </div>
        ) : conversationItems.length ? (
          <>
            <div className="flex-1 space-y-1 overflow-y-auto">
              {conversationItems.map((item) => (
                <div
                  key={item.id}
                  className={`group flex items-center gap-1 rounded-xl ${conversation?.id === item.id ? 'bg-pink-surface' : 'hover:bg-background-secondary'}`}
                >
                  <button
                    type="button"
                    onClick={() => openConversation(item.id)}
                    className="min-w-0 flex-1 text-left px-3 py-2.5"
                  >
                    <p className="text-xs font-bold text-foreground truncate">{item.title}</p>
                    <p className="text-[11px] text-foreground-secondary mt-0.5">{item.message_count} messages</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => removeConversation(item.id)}
                    className="p-2 mr-1 text-foreground-secondary opacity-0 group-hover:opacity-100 hover:text-red-600"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
            {totalPages > 1 && (
              <div className="pt-3 flex items-center justify-between text-[11px] text-foreground-secondary">
                <button type="button" disabled={page <= 1} onClick={() => loadList(page - 1)} className="p-1.5 disabled:opacity-40">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span>{page} / {totalPages}</span>
                <button type="button" disabled={page >= totalPages} onClick={() => loadList(page + 1)} className="p-1.5 disabled:opacity-40">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-center px-3">
            <p className="text-xs text-foreground-secondary">No conversations yet.</p>
          </div>
        )}
      </aside>

      <section className="knit-glass-panel border border-border/80 rounded-[22px] overflow-hidden flex flex-col min-h-[600px] xl:h-[calc(100vh-160px)] shadow-soft">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-pink-surface flex items-center justify-center text-coral">
              <Sparkles className="w-4.5 h-4.5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-foreground">KNIT AI Assistant</h2>
              <p className="text-[11px] text-foreground-secondary">Questions grounded in your authorized emails</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {!conversation && (
            <div className="max-w-xl mx-auto pt-8 text-center space-y-5">
              <div className="w-14 h-14 rounded-2xl bg-pink-surface text-coral flex items-center justify-center mx-auto">
                <MessageSquare className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">Ask about your inbox</h3>
                <p className="text-xs text-foreground-secondary mt-1">
                  Answers use only the emails in your connected mailbox.
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setMessage(suggestion)}
                    className="text-left text-xs text-foreground-secondary border border-border rounded-xl px-3 py-3 hover:border-coral/40 hover:bg-pink-surface/40"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {conversation?.messages.map((item) => (
            <div key={item.id} className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[82%] rounded-[18px] px-4 py-3.5 ${item.role === 'user' ? 'bg-coral text-white shadow-coral-sm animate-in fade-in slide-in-from-right-2 duration-300' : 'bg-white border border-border text-foreground shadow-soft animate-in fade-in slide-in-from-bottom-2 duration-500'}`}>
                {item.role === 'assistant' ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h2: ({ children }) => <h2 className="mt-1 mb-2 text-base font-extrabold text-foreground">{children}</h2>,
                      h3: ({ children }) => <h3 className="mt-3 mb-1.5 text-sm font-bold text-foreground">{children}</h3>,
                      p: ({ children }) => <p className="mb-2 text-sm leading-6 text-foreground last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="font-bold text-foreground">{children}</strong>,
                      ul: ({ children }) => <ul className="mb-2 ml-5 list-disc space-y-1 text-sm leading-6 text-foreground">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-2 ml-5 list-decimal space-y-1 text-sm leading-6 text-foreground">{children}</ol>,
                      li: ({ children }) => <li className="break-words">{children}</li>,
                      blockquote: ({ children }) => <blockquote className="my-2 border-l-2 border-coral pl-3 text-sm italic text-foreground-secondary">{children}</blockquote>,
                      table: ({ children }) => <div className="my-3 overflow-x-auto rounded-lg border border-border"><table className="w-full border-collapse text-xs">{children}</table></div>,
                      thead: ({ children }) => <thead className="bg-white/70">{children}</thead>,
                      th: ({ children }) => <th className="border-b border-border px-3 py-2 text-left font-bold text-foreground">{children}</th>,
                      td: ({ children }) => <td className="border-b border-border px-3 py-2 align-top text-foreground-secondary last:border-b-0">{children}</td>,
                      code: ({ children }) => <code className="rounded bg-white px-1.2 py-0.5 font-mono text-xs text-coral">{children}</code>,
                      pre: ({ children }) => <pre className="my-2 overflow-x-auto rounded-lg bg-white p-3 text-xs">{children}</pre>,
                      a: ({ children, href }) => <a href={href} target="_blank" rel="noreferrer" className="font-medium text-coral underline underline-offset-2">{children}</a>,
                    }}
                  >
                    {item.content}
                  </ReactMarkdown>
                ) : (
                  <p className="text-sm whitespace-pre-wrap break-words">{item.content}</p>
                )}
                {item.role === 'assistant' && item.references.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border space-y-1">
                    <p className="text-[11px] font-bold text-coral">Source emails</p>
                    {item.references.map((reference) => (
                      <button
                        key={reference.email_id}
                        type="button"
                        onClick={() => navigate(`/app/inbox/${reference.email_id}`)}
                        className="block text-left text-xs text-foreground-secondary hover:text-coral"
                      >
                        {reference.subject} — {reference.sender_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loadingConversation && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-pink-surface/60 border border-border px-4 py-3">
                <LoaderCircle className="w-4 h-4 animate-spin text-coral" />
              </div>
            </div>
          )}

          {sending && (
            <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="knit-thinking rounded-2xl border border-border bg-white px-4 py-3 shadow-soft" aria-label="KNIT is thinking">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700 flex items-center justify-between gap-3">
              <span>{error}</span>
              <button type="button" onClick={() => retryPrompt && void sendContent(retryPrompt)} className="text-red-700 font-bold flex items-center gap-1">
                <RefreshCw className="w-3.5 h-3.5" /> Retry
              </button>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={submitMessage} className="border-t border-border p-3 sm:p-4 flex items-end gap-2">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault()
                if (message.trim() && !sending) {
                  void sendContent(message)
                }
              }
            }}
            placeholder="Ask about your emails..."
            rows={2}
            maxLength={4000}
            className="flex-1 resize-none bg-background-secondary border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-foreground-secondary/60 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral"
          />
          <Button type="submit" variant="primary" size="md" disabled={sending || !message.trim()} className="h-11">
            {sending ? <LoaderCircle className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span className="hidden sm:inline">Send</span>
          </Button>
        </form>
      </section>
    </div>
  )
}
