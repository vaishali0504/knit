import React, { useEffect, useRef, useState } from 'react'
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
import { Badge } from '../../components/ui/Badge'
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
    const content = message.trim()
    if (!content) return

    setSending(true)
    setError(null)
    try {
      let active = conversation
      if (!active) {
        active = await createConversation(content.slice(0, 80))
        setConversation(active)
      }
      const assistantMessage = await sendAssistantMessage(active.id, content)
      void assistantMessage
      setConversation(await getConversation(active.id))
      setMessage('')
      await loadList(1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to send your question.')
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

      <section className="bg-white border border-border rounded-2xl overflow-hidden flex flex-col min-h-[600px] xl:h-[calc(100vh-160px)]">
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
          <Badge variant="pink" size="sm">Demo inbox</Badge>
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
                  Answers use only your authorized sample email records.
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
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${item.role === 'user' ? 'bg-coral text-white' : 'bg-pink-surface/60 border border-border text-foreground'}`}>
                <p className="text-sm whitespace-pre-wrap break-words">{item.content}</p>
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

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700 flex items-center justify-between gap-3">
              <span>{error}</span>
              <button type="button" onClick={() => loadList(page)} className="text-red-700 font-bold flex items-center gap-1">
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
