export type ConnectionTone = 'success' | 'coral' | 'warning' | 'neutral'
export type SyncOutcomeKind = 'reconnect' | 'full-resync' | 'success' | 'retry'

export function connectionStatusPresentation(status: string): { label: string; tone: ConnectionTone }
export function syncOutcomePresentation(result: { status?: string; error_code?: string | null; message?: string | null }): { kind: SyncOutcomeKind; message: string }
export function syncCountsMessage(result: { sync_type: string; added: number; updated: number; removed: number }): string
export function disconnectConfirmation(emailAddress: string): string
export function acquireSyncLock(activeIds: Set<number>, accountId: number): boolean
export function releaseSyncLock(activeIds: Set<number>, accountId: number): void
