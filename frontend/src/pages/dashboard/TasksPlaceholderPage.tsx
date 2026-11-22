import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock3,
  Edit3,
  LoaderCircle,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  X,
} from 'lucide-react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { createTask, deleteTask, listTasks, updateTask } from '../../services/tasks'
import type { Task, TaskCreateData, TaskPriority, TaskStatus } from '../../types/task'

function formatDate(value: string | null): string {
  if (!value) return 'No deadline'
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function priorityVariant(priority: TaskPriority): 'warning' | 'coral' | 'neutral' {
  if (priority === 'high') return 'coral'
  if (priority === 'medium') return 'warning'
  return 'neutral'
}

export const TasksPlaceholderPage: React.FC = () => {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<TaskStatus | 'all'>('all')
  const [priority, setPriority] = useState<TaskPriority | 'all'>('all')
  const [sort, setSort] = useState<'due' | 'oldest' | 'priority'>('due')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [refreshKey, setRefreshKey] = useState(0)
  const [editorOpen, setEditorOpen] = useState(false)
  const [editing, setEditing] = useState<Task | null>(null)
  const [form, setForm] = useState<TaskCreateData>({
    title: '',
    description: '',
    due_at: null,
    priority: 'medium',
    status: 'pending',
  })

  useEffect(() => {
    let cancelled = false
    listTasks({
      status: status === 'all' ? undefined : status,
      priority: priority === 'all' ? undefined : priority,
      search: search.trim() || undefined,
      sort,
      page,
      pageSize: 20,
    })
      .then((result) => {
        if (!cancelled) {
          setTasks(result.items)
          setTotal(result.total)
          setTotalPages(result.total_pages)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load tasks.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [status, priority, search, sort, page, refreshKey])

  const upcoming = useMemo(() => {
    return tasks
      .filter((task) => task.status !== 'completed' && task.due_at)
      .sort((a, b) => new Date(a.due_at as string).getTime() - new Date(b.due_at as string).getTime())
      .slice(0, 5)
  }, [tasks])

  const openCreate = () => {
    setEditing(null)
    setForm({ title: '', description: '', due_at: null, priority: 'medium', status: 'pending' })
    setEditorOpen(true)
  }

  const openEdit = (task: Task) => {
    setEditing(task)
    setForm({
      title: task.title,
      description: task.description,
      due_at: task.due_at ? task.due_at.slice(0, 16) : null,
      priority: task.priority,
      status: task.status,
      source_email_id: task.source_email_id,
    })
    setEditorOpen(true)
  }

  const submitEditor = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!form.title.trim()) return
    setLoading(true)
    setError(null)
    try {
      const payload: TaskCreateData = {
        ...form,
        title: form.title.trim(),
        description: form.description?.trim() || null,
        due_at: form.due_at ? new Date(form.due_at).toISOString() : null,
      }
      if (editing) await updateTask(editing.id, payload)
      else await createTask(payload)
      setEditorOpen(false)
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save task.')
    } finally {
      setLoading(false)
    }
  }

  const toggleCompleted = async (task: Task) => {
    try {
      await updateTask(task.id, { status: task.status === 'completed' ? 'pending' : 'completed' })
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update task.')
    }
  }

  const removeTask = async (task: Task) => {
    if (!window.confirm(`Delete "${task.title}"?`)) return
    try {
      await deleteTask(task.id)
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to delete task.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">Tasks & Deadlines</h1>
            <Badge variant="pink" size="sm">Personal tasks</Badge>
          </div>
          <p className="text-xs sm:text-sm text-foreground-secondary mt-1">
            Manage important commitments and upcoming deadlines.
          </p>
        </div>
        <Button variant="primary" size="md" onClick={openCreate}>
          <Plus className="w-4 h-4" />
          Add task
        </Button>
      </div>

      {upcoming.length > 0 && (
        <section className="bg-pink-surface/60 border border-border rounded-2xl p-4 sm:p-5">
          <div className="flex items-center gap-2 mb-3">
            <CalendarDays className="w-4 h-4 text-coral" />
            <h2 className="text-sm font-bold text-foreground">Upcoming deadlines</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {upcoming.map((task) => (
              <button
                key={task.id}
                type="button"
                onClick={() => openEdit(task)}
                className="text-left rounded-xl bg-white border border-border p-3 hover:border-coral/40 transition-colors"
              >
                <p className="text-xs font-bold text-foreground truncate">{task.title}</p>
                <p className="text-[11px] text-coral mt-1">{formatDate(task.due_at)}</p>
              </button>
            ))}
          </div>
        </section>
      )}

      <div className="bg-white border border-border rounded-2xl p-3 flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-secondary" />
          <input
            value={search}
            onChange={(event) => { setSearch(event.target.value); setPage(1) }}
            placeholder="Search tasks..."
            className="w-full bg-background-secondary border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral"
          />
        </div>
        <select value={status} onChange={(event) => { setStatus(event.target.value as TaskStatus | 'all'); setPage(1) }} className="bg-white border border-border rounded-xl px-3 py-2.5 text-sm">
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In progress</option>
          <option value="completed">Completed</option>
        </select>
        <select value={priority} onChange={(event) => { setPriority(event.target.value as TaskPriority | 'all'); setPage(1) }} className="bg-white border border-border rounded-xl px-3 py-2.5 text-sm">
          <option value="all">All priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select value={sort} onChange={(event) => setSort(event.target.value as 'due' | 'oldest' | 'priority')} className="bg-white border border-border rounded-xl px-3 py-2.5 text-sm">
          <option value="due">Due date</option>
          <option value="oldest">Newest / oldest</option>
          <option value="priority">Priority</option>
        </select>
        <Button variant="secondary" size="sm" onClick={() => setRefreshKey((value) => value + 1)}>
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
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
      ) : tasks.length ? (
        <>
          <div className="bg-white border border-border rounded-2xl overflow-hidden divide-y divide-border">
            {tasks.map((task) => (
              <div key={task.id} className="px-4 sm:px-5 py-4 flex items-start gap-3">
                <button
                  type="button"
                  onClick={() => toggleCompleted(task)}
                  className="mt-0.5 text-coral hover:text-coral-hover"
                  aria-label={task.status === 'completed' ? 'Mark task pending' : 'Mark task completed'}
                >
                  {task.status === 'completed' ? <CheckCircle2 className="w-5 h-5 fill-coral-light" /> : <Circle className="w-5 h-5" />}
                </button>
                <button type="button" onClick={() => openEdit(task)} className="min-w-0 flex-1 text-left">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className={`text-sm font-bold ${task.status === 'completed' ? 'text-foreground-secondary line-through' : 'text-foreground'}`}>{task.title}</p>
                    <Badge variant={priorityVariant(task.priority)} size="sm">{task.priority}</Badge>
                    <Badge variant="neutral" size="sm">{task.status.replace('_', ' ')}</Badge>
                  </div>
                  {task.description && <p className="text-xs text-foreground-secondary mt-1 line-clamp-2">{task.description}</p>}
                  <div className="flex items-center gap-3 mt-2 text-[11px] text-foreground-secondary">
                    <span className="flex items-center gap-1"><Clock3 className="w-3.5 h-3.5" />{formatDate(task.due_at)}</span>
                    {task.source_email && (
                      <button type="button" onClick={(event) => { event.stopPropagation(); navigate(`/app/inbox/${task.source_email_id}`) }} className="text-coral hover:text-coral-hover">
                        Source: {task.source_email.subject}
                      </button>
                    )}
                  </div>
                </button>
                <div className="flex items-center gap-1">
                  <button type="button" onClick={() => openEdit(task)} className="p-2 rounded-lg text-foreground-secondary hover:text-coral hover:bg-pink-surface" title="Edit task">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button type="button" onClick={() => removeTask(task)} className="p-2 rounded-lg text-foreground-secondary hover:text-red-600 hover:bg-red-50" title="Delete task">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>{total} tasks</span>
              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
                  <ChevronLeft className="w-4 h-4" /> Previous
                </Button>
                <span>Page {page} of {totalPages}</span>
                <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>
                  Next <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white border border-border rounded-2xl p-12 text-center space-y-3">
          <CheckCircle2 className="w-8 h-8 text-coral mx-auto" />
          <h2 className="text-base font-bold text-foreground">No tasks match these filters</h2>
          <p className="text-sm text-foreground-secondary">Create a task or adjust the filters.</p>
        </div>
      )}

      {editorOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-foreground/40" onClick={() => setEditorOpen(false)} />
          <form onSubmit={submitEditor} className="relative w-full max-w-lg bg-white border border-border rounded-2xl shadow-xl p-5 sm:p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-foreground">{editing ? 'Edit task' : 'Create task'}</h2>
              <button type="button" onClick={() => setEditorOpen(false)} className="p-2 rounded-lg text-foreground-secondary hover:bg-background-secondary">
                <X className="w-4 h-4" />
              </button>
            </div>
            <label className="block text-xs font-bold text-foreground">Title
              <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required maxLength={255} className="mt-1.5 w-full border border-border rounded-xl px-3 py-2.5 text-sm" />
            </label>
            <label className="block text-xs font-bold text-foreground">Description
              <textarea value={form.description || ''} onChange={(event) => setForm({ ...form, description: event.target.value })} maxLength={5000} rows={4} className="mt-1.5 w-full border border-border rounded-xl px-3 py-2.5 text-sm resize-y" />
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label className="text-xs font-bold text-foreground">Due date
                <input type="datetime-local" value={form.due_at || ''} onChange={(event) => setForm({ ...form, due_at: event.target.value || null })} className="mt-1.5 w-full border border-border rounded-xl px-3 py-2.5 text-xs" />
              </label>
              <label className="text-xs font-bold text-foreground">Priority
                <select value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value as TaskPriority })} className="mt-1.5 w-full border border-border rounded-xl px-3 py-2.5 text-xs">
                  <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
                </select>
              </label>
              <label className="text-xs font-bold text-foreground">Status
                <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as TaskStatus })} className="mt-1.5 w-full border border-border rounded-xl px-3 py-2.5 text-xs">
                  <option value="pending">Pending</option><option value="in_progress">In progress</option><option value="completed">Completed</option>
                </select>
              </label>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" size="md" type="button" onClick={() => setEditorOpen(false)}>Cancel</Button>
              <Button variant="primary" size="md" type="submit">{editing ? 'Save changes' : 'Create task'}</Button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
