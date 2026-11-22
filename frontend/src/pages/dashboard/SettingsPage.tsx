import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Mail,
  CheckCircle2,
  Clock,
  Info,
  RefreshCw,
  RotateCcw,
  Sparkles,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { ConnectionApiError, disconnectAccount, getGmailConnectionStatus, listConnectedAccounts, startGmailAuthorization, syncAccount, updateGmailSyncSettings, type ConnectedAccount } from '../../services/connections'
import { checkAIConnection } from '../../services/ai'
import { acquireSyncLock, connectionStatusPresentation, disconnectConfirmation, releaseSyncLock, syncCountsMessage, syncOutcomePresentation } from '../../services/connectionPresentation.js'

type SyncFeedback = { kind: 'success' | 'retry' | 'reconnect' | 'full-resync'; message: string; counts?: string }

export const SettingsPage: React.FC = () => {
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [working, setWorking] = useState(false)
  const [disconnectingId, setDisconnectingId] = useState<number | null>(null)
  const [syncingIds, setSyncingIds] = useState<Set<number>>(() => new Set())
  const syncingRef = useRef<Set<number>>(new Set())
  const [syncFeedback, setSyncFeedback] = useState<Record<number, SyncFeedback>>({})
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [gmailStatus, setGmailStatus] = useState<{ enabled: boolean; credentials_configured: boolean; sync_max_messages: number; sync_page_size: number } | null>(null)
  const [syncMaxMessages, setSyncMaxMessages] = useState(100)
  const [syncPageSize, setSyncPageSize] = useState(25)
  const [savingSyncSettings, setSavingSyncSettings] = useState(false)
  const [aiChecking, setAiChecking] = useState(false)
  const [aiNotice, setAiNotice] = useState<string | null>(null)

  const refreshAccounts = useCallback(async () => {
    const result = await listConnectedAccounts()
    setAccounts(result)
    return result
  }, [])

  useEffect(() => {
    let active = true
    // This effect performs the authenticated account-list request on mount.
    // oxlint-disable-next-line react/set-state-in-effect
    refreshAccounts().then(() => {
      if (active) setError(null)
    }).catch((err: unknown) => {
      if (active) setError(err instanceof Error ? err.message : 'Unable to load connected accounts.')
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [refreshAccounts])

  useEffect(() => {
    getGmailConnectionStatus()
      .then((status) => {
        setGmailStatus(status)
        setSyncMaxMessages(status.sync_max_messages)
        setSyncPageSize(status.sync_page_size)
      })
      .catch(() => setGmailStatus(null))
  }, [])

  const callbackResult = searchParams.get('gmail')
  const callbackNotice = callbackResult ? (
    callbackResult === 'connected' ? 'Gmail connected successfully.' :
      callbackResult === 'denied' ? 'Google authorization was cancelled.' :
        'Gmail connection could not be completed.'
  ) : null

  const connectGmail = async () => {
    setWorking(true)
    setError(null)
    try {
      const { authorization_url } = await startGmailAuthorization()
      window.location.assign(authorization_url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start Gmail authorization.')
      setWorking(false)
    }
  }

  const disconnectGmail = async (account: ConnectedAccount) => {
    if (!window.confirm(disconnectConfirmation(account.email_address))) return
    setWorking(true)
    setDisconnectingId(account.id)
    setError(null)
    try {
      await disconnectAccount(account.id)
      setAccounts((current) => current.filter((item) => item.id !== account.id))
      setSyncFeedback((current) => { const next = { ...current }; delete next[account.id]; return next })
      setNotice('Gmail disconnected. Existing KNIT emails and tasks were kept.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to disconnect Gmail.')
    } finally {
      setWorking(false)
      setDisconnectingId(null)
    }
  }

  const syncGmail = async (account: ConnectedAccount) => {
    if (!acquireSyncLock(syncingRef.current, account.id)) return
    setSyncingIds(new Set(syncingRef.current))
    setSyncFeedback((current) => { const next = { ...current }; delete next[account.id]; return next })
    setError(null)
    setNotice(null)
    try {
      const result = await syncAccount(account.id)
      const outcome = syncOutcomePresentation(result)
      setSyncFeedback((current) => ({
        ...current,
        [account.id]: {
          kind: outcome.kind,
          message: outcome.kind === 'success' ? 'Gmail sync completed.' : outcome.message,
          counts: syncCountsMessage(result),
        },
      }))
      try {
        await refreshAccounts()
      } catch {
        setError('Sync finished, but connection status could not be refreshed. Refresh Settings to see the latest status.')
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Gmail sync could not be completed.'
      const reconnect = err instanceof ConnectionApiError && err.statusCode === 401 && message.toLowerCase().includes('reconnect')
      const outcome = syncOutcomePresentation({
        status: 'error',
        error_code: reconnect ? 'reauthorization_required' : null,
        message,
      })
      setSyncFeedback((current) => ({ ...current, [account.id]: { kind: outcome.kind, message: outcome.message } }))
      try { await refreshAccounts() } catch { /* Keep the original sync error visible. */ }
    } finally {
      releaseSyncLock(syncingRef.current, account.id)
      setSyncingIds(new Set(syncingRef.current))
    }
  }

  const testAIConnection = async () => {
    setAiChecking(true)
    setAiNotice(null)
    try {
      const result = await checkAIConnection()
      setAiNotice(`Gemini connected successfully using ${result.model}.`)
    } catch (err) {
      setAiNotice(err instanceof Error ? err.message : 'Gemini connection check failed.')
    } finally {
      setAiChecking(false)
    }
  }

  const saveSyncSettings = async () => {
    if (syncPageSize > syncMaxMessages) {
      setNotice('Sync page size cannot exceed the maximum messages per sync.')
      return
    }
    setSavingSyncSettings(true)
    setNotice(null)
    try {
      const status = await updateGmailSyncSettings(syncMaxMessages, syncPageSize)
      setGmailStatus(status)
      setSyncMaxMessages(status.sync_max_messages)
      setSyncPageSize(status.sync_page_size)
      setNotice('Gmail sync settings saved.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save Gmail sync settings.')
    } finally {
      setSavingSyncSettings(false)
    }
  }

  return (
    <div className="space-y-8 max-w-4xl animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">
          Settings & Connected Accounts
        </h1>
        <p className="text-xs sm:text-sm text-foreground-secondary mt-1">
          Manage your KNIT user profile, security settings, and external email integrations.
        </p>
      </div>

      {/* Connected Accounts Section (Crucial Phase 3 requirement) */}
      <Card className="p-4 sm:p-8 bg-white border border-border space-y-6">
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-border">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-foreground">Connected Accounts</h2>
              <Badge variant="coral" size="sm">
                Integrations
              </Badge>
            </div>
            <p className="text-xs sm:text-sm text-foreground-secondary mt-1">
              Connect external email providers to enable AI intelligence over your mailbox.
            </p>
          </div>
        </div>

        {/* Gmail Integration Card */}
        <div className="rounded-2xl border-2 border-dashed border-border p-4 sm:p-6 bg-background-secondary/40 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-xl bg-white border border-border flex items-center justify-center text-red-500 shadow-xs">
                <Mail className="w-6 h-6 text-coral" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-base text-foreground">Google Gmail</h3>
                  <Badge variant={accounts.length ? 'coral' : 'neutral'} size="sm">
                    {accounts.length ? 'Connected' : <><Clock className="w-3 h-3 mr-1" />Not connected</>}
                  </Badge>
                </div>
                <p className="text-xs text-foreground-secondary mt-0.5">Read-only Gmail sync through Google OAuth 2.0</p>
              </div>
            </div>

            {accounts.length === 0 ? (
              <Button variant="secondary" size="sm" disabled={working || loading || gmailStatus?.enabled === false} onClick={() => void connectGmail()} className="self-start sm:self-auto">
                {working ? 'Opening Google…' : 'Connect Gmail'}
              </Button>
            ) : null}
          </div>

          {loading && <p className="text-xs text-foreground-secondary" role="status" aria-live="polite">Loading connected accounts…</p>}
          {error && <div className="rounded-lg bg-red-50 p-3 text-xs text-red-700" role="alert"><p>{error}</p>{!loading && accounts.length === 0 && <Button variant="ghost" size="sm" className="mt-2" onClick={() => { setLoading(true); setError(null); void refreshAccounts().catch((err: unknown) => setError(err instanceof Error ? err.message : 'Unable to load connected accounts.')).finally(() => setLoading(false)) }}>Try again</Button>}</div>}
          {(notice || callbackNotice) && <p className="rounded-lg bg-background-secondary p-3 text-xs text-foreground-secondary" role="status">{notice || callbackNotice}</p>}
          {!loading && !error && accounts.length === 0 && <div className="rounded-xl border border-border bg-white p-4 text-sm text-foreground-secondary" role="status">{gmailStatus?.enabled === false ? 'Gmail connection is not enabled yet. Configure the Google OAuth credentials and Gmail integration setting in the backend environment.' : 'No Gmail account is connected. Connect an account to import read-only email data into KNIT.'}</div>}
          {accounts.map((account) => (
            <div key={account.id} className="space-y-3 rounded-xl border border-border bg-white p-4">
              <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <p className="break-all text-sm font-semibold text-foreground">{account.email_address}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <Badge size="sm" variant={connectionStatusPresentation(syncingIds.has(account.id) ? 'syncing' : account.status).tone as 'success' | 'coral' | 'warning' | 'neutral'}>
                      {syncingIds.has(account.id) ? 'Syncing' : connectionStatusPresentation(account.status).label}
                    </Badge>
                    <span className="text-xs text-foreground-secondary">Last successful sync: {account.last_successful_sync_at ? new Date(account.last_successful_sync_at).toLocaleString() : 'Never'}</span>
                  </div>
                </div>
                <div className="flex w-full flex-wrap gap-2 sm:w-auto sm:justify-end">
                  {syncFeedback[account.id]?.kind === 'reconnect' ? (
                    <Button variant="primary" size="sm" disabled={working || syncingIds.has(account.id)} onClick={() => void connectGmail()} aria-label="Reconnect Gmail">Reconnect</Button>
                  ) : (
                    <Button variant="primary" size="sm" disabled={working || syncingIds.has(account.id) || loading} onClick={() => void syncGmail(account)} aria-label={account.status === 'full_resync_required' ? 'Run full Gmail resync' : 'Sync Gmail now'}>
                      {syncingIds.has(account.id) ? <><RefreshCw className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />Syncing…</> : account.status === 'full_resync_required' ? 'Run full resync' : syncFeedback[account.id]?.kind === 'retry' || account.status === 'error' || account.status === 'partial' ? <><RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />Retry sync</> : <><RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />Sync now</>}
                    </Button>
                  )}
                  {account.status === 'error' && syncFeedback[account.id]?.kind !== 'reconnect' && <Button variant="ghost" size="sm" disabled={working || syncingIds.has(account.id)} onClick={() => void connectGmail()} aria-label="Reconnect Gmail">Reconnect</Button>}
                  <Button variant="secondary" size="sm" disabled={working || syncingIds.has(account.id)} onClick={() => void disconnectGmail(account)} aria-label={`Disconnect ${account.email_address}`}>
                    {disconnectingId === account.id ? 'Disconnecting…' : 'Disconnect'}
                  </Button>
                </div>
              </div>
              {syncFeedback[account.id] && <div className={`rounded-lg p-3 text-xs ${syncFeedback[account.id].kind === 'success' ? 'bg-emerald-50 text-emerald-800' : syncFeedback[account.id].kind === 'retry' || syncFeedback[account.id].kind === 'reconnect' ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-800'}`} role={syncFeedback[account.id].kind === 'success' ? 'status' : 'alert'} aria-live="polite">
                <p>{syncFeedback[account.id].message}</p>
                {syncFeedback[account.id].counts && <p className="mt-1 font-medium">{syncFeedback[account.id].counts}</p>}
              </div>}
            </div>
          ))}

          <div className="rounded-xl border border-border bg-white p-4">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-foreground">Gmail Sync Settings</h3>
              <p className="mt-1 text-xs text-foreground-secondary">Control how much Gmail data is imported during each sync.</p>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
              <label className="text-xs font-bold text-foreground">
                Maximum messages per sync
                <input
                  type="number"
                  min={1}
                  max={500}
                  value={syncMaxMessages}
                  onChange={(event) => setSyncMaxMessages(Math.min(500, Math.max(1, Number(event.target.value) || 1)))}
                  className="mt-1.5 w-full rounded-xl border border-border bg-white px-3 py-2 text-sm font-normal text-foreground focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral/20"
                />
              </label>
              <label className="text-xs font-bold text-foreground">
                Messages per page
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={syncPageSize}
                  onChange={(event) => setSyncPageSize(Math.min(100, Math.max(1, Number(event.target.value) || 1)))}
                  className="mt-1.5 w-full rounded-xl border border-border bg-white px-3 py-2 text-sm font-normal text-foreground focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral/20"
                />
              </label>
              <Button type="button" variant="secondary" size="sm" disabled={savingSyncSettings} onClick={() => void saveSyncSettings()}>
                {savingSyncSettings ? 'Saving…' : 'Save settings'}
              </Button>
            </div>
          </div>

          <div className="rounded-xl bg-white border border-border p-4 text-xs text-foreground-secondary space-y-2">
            <div className="flex items-center gap-2 text-foreground font-semibold">
              <Info className="w-4 h-4 text-coral" />
              <span>How Gmail Integration Works</span>
            </div>
            <p className="leading-relaxed">
              Connect Gmail through Google&apos;s official OAuth 2.0 flow. KNIT uses read-only mailbox access, and disconnecting preserves imported emails and tasks in KNIT:
            </p>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-medium text-foreground">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Minimum read-only permissions</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Zero auto-sending guarantee</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Backend token encryption</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Full revocation control</span>
              </li>
            </ul>
          </div>
        </div>
      </Card>

      <Card className="p-6 sm:p-8 bg-white border border-border space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-coral" />
              <h2 className="text-lg font-bold text-foreground">AI Provider Connection</h2>
            </div>
            <p className="mt-1 text-xs sm:text-sm text-foreground-secondary">
              Verify that the backend can reach Gemini with the configured API key.
            </p>
          </div>
          <Button variant="secondary" size="sm" disabled={aiChecking} onClick={() => void testAIConnection()}>
            {aiChecking ? 'Testing…' : 'Test connection'}
          </Button>
        </div>
        {aiNotice && (
          <p className="rounded-lg bg-background-secondary p-3 text-xs text-foreground-secondary" role="status">
            {aiNotice}
          </p>
        )}
      </Card>

      {/* User Profile Information */}
      <Card className="p-6 sm:p-8 bg-white border border-border space-y-6">
        <div className="pb-4 border-b border-border">
          <h2 className="text-lg font-bold text-foreground">User Profile</h2>
          <p className="text-xs sm:text-sm text-foreground-secondary mt-1">
            Your authenticated KNIT credentials and account details.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-background-secondary border border-border">
            <span className="text-foreground-secondary block mb-1">Email Address</span>
            <span className="font-bold text-sm text-foreground block">{user?.email}</span>
          </div>

          <div className="p-4 rounded-xl bg-background-secondary border border-border">
            <span className="text-foreground-secondary block mb-1">Full Name</span>
            <span className="font-bold text-sm text-foreground block">
              {user?.full_name || 'Not provided'}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-background-secondary border border-border">
            <span className="text-foreground-secondary block mb-1">User Account ID</span>
            <span className="font-mono font-bold text-sm text-foreground block">#{user?.id}</span>
          </div>

          <div className="p-4 rounded-xl bg-background-secondary border border-border">
            <span className="text-foreground-secondary block mb-1">Account Created</span>
            <span className="font-bold text-sm text-foreground block">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}
            </span>
          </div>
        </div>
      </Card>
    </div>
  )
}
