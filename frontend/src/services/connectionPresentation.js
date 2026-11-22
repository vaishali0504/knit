/** @typedef {{status?: string, error_code?: string | null, message?: string | null}} SyncState */

/** @param {string} status */
export function connectionStatusPresentation(status) {
  switch (status) {
    case 'complete': return { label: 'Connected · Synced', tone: 'success' }
    case 'syncing': return { label: 'Syncing', tone: 'coral' }
    case 'initial_sync_pending': return { label: 'Initial sync pending', tone: 'warning' }
    case 'incremental_sync_pending': return { label: 'More changes pending', tone: 'warning' }
    case 'full_resync_required': return { label: 'Full resync required', tone: 'warning' }
    case 'partial': return { label: 'Partially synced', tone: 'warning' }
    case 'error': return { label: 'Sync needs attention', tone: 'warning' }
    case 'pending': return { label: 'Connected · Not synced', tone: 'neutral' }
    default: return { label: 'Connected', tone: 'neutral' }
  }
}

/** @param {SyncState} result */
export function syncOutcomePresentation(result) {
  if (result.error_code === 'reauthorization_required') {
    return { kind: 'reconnect', message: 'Gmail authorization expired or was revoked. Reconnect Gmail to continue syncing.' }
  }
  if (result.status === 'full_resync_required' || result.error_code === 'history_cursor_invalid') {
    return { kind: 'full-resync', message: 'Gmail history expired. Run a full resynchronization to restore complete mailbox data.' }
  }
  if (result.status === 'complete') return { kind: 'success', message: '' }
  return {
    kind: 'retry',
    message: result.message || 'Sync could not be completed. You can safely try again.',
  }
}

/** @param {{sync_type: string, added: number, updated: number, removed: number}} result */
export function syncCountsMessage(result) {
  const syncLabel = result.sync_type === 'initial' ? 'Initial sync' : 'Incremental sync'
  return `${syncLabel}: ${result.added} added, ${result.updated} updated, ${result.removed} removed.`
}

/** @param {string} emailAddress */
export function disconnectConfirmation(emailAddress) {
  return `Disconnect ${emailAddress} from KNIT? This removes the Gmail connection but preserves imported KNIT emails and tasks.`
}

/** @param {Set<number>} activeIds @param {number} accountId */
export function acquireSyncLock(activeIds, accountId) {
  if (activeIds.has(accountId)) return false
  activeIds.add(accountId)
  return true
}

/** @param {Set<number>} activeIds @param {number} accountId */
export function releaseSyncLock(activeIds, accountId) {
  activeIds.delete(accountId)
}
