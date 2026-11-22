import assert from 'node:assert/strict'
import test from 'node:test'
import {
  connectionStatusPresentation,
  disconnectConfirmation,
  acquireSyncLock,
  releaseSyncLock,
  syncCountsMessage,
  syncOutcomePresentation,
} from '../src/services/connectionPresentation.js'

test('connection status covers initial, synced, pending, and full-resync states', () => {
  assert.equal(connectionStatusPresentation('pending').label, 'Connected · Not synced')
  assert.equal(connectionStatusPresentation('complete').tone, 'success')
  assert.equal(connectionStatusPresentation('syncing').label, 'Syncing')
  assert.equal(connectionStatusPresentation('full_resync_required').label, 'Full resync required')
})

test('sync results describe initial and incremental counts', () => {
  assert.equal(syncCountsMessage({ sync_type: 'initial', added: 4, updated: 0, removed: 0 }), 'Initial sync: 4 added, 0 updated, 0 removed.')
  assert.equal(syncCountsMessage({ sync_type: 'incremental', added: 1, updated: 2, removed: 3 }), 'Incremental sync: 1 added, 2 updated, 3 removed.')
})

test('sync failures offer retry, reconnect, or full-resync guidance', () => {
  assert.equal(syncOutcomePresentation({ status: 'partial', message: 'Try again later.' }).kind, 'retry')
  assert.equal(syncOutcomePresentation({ status: 'error', error_code: 'reauthorization_required' }).kind, 'reconnect')
  assert.equal(syncOutcomePresentation({ status: 'full_resync_required' }).kind, 'full-resync')
  assert.equal(syncOutcomePresentation({ status: 'complete' }).kind, 'success')
})

test('disconnect confirmation explains that KNIT data is preserved', () => {
  const message = disconnectConfirmation('owner@example.test')
  assert.match(message, /owner@example\.test/)
  assert.match(message, /preserves imported KNIT emails and tasks/)
})

test('sync lock rejects duplicate actions for the same account and releases after completion', () => {
  const activeIds = new Set()
  assert.equal(acquireSyncLock(activeIds, 7), true)
  assert.equal(acquireSyncLock(activeIds, 7), false)
  assert.equal(acquireSyncLock(activeIds, 8), true)
  releaseSyncLock(activeIds, 7)
  assert.equal(acquireSyncLock(activeIds, 7), true)
})
