# KNIT — Development Tasks and Implementation Roadmap

## 1. Development Approach

Build KNIT incrementally using the approved requirements and architecture.

Development must follow a phase-by-phase approach.

Rules:
- Complete one phase at a time.
- Break large tasks into smaller tasks.
- Test each major feature before moving forward.
- Reuse existing components and services.
- Do not implement future-phase features early.
- Do not mark incomplete work as completed.
- Ask for approval before moving into a new major phase.

## 2. Phase 0 — Project Setup and Analysis

- [x] Read PRD.md.
- [x] Read ARCHITECTURE.md.
- [x] Read RULES.md.
- [x] Read DESIGN.md.
- [x] Read TASKS.md.
- [x] Read MEMORY.md if available.
- [x] Inspect the existing project files.
- [x] Identify missing requirements or conflicting instructions.
- [x] Propose the implementation plan.
- [x] Wait for user approval before coding.

## 3. Phase 1 — Foundation and Project Setup

- [x] Initialize frontend using React, Vite and TypeScript.
- [x] Configure Tailwind CSS.
- [x] Install and configure Lucide React.
- [x] Install and configure Framer Motion.
- [x] Set up the Python FastAPI backend.
- [x] Configure Pydantic and SQLAlchemy.
- [x] Configure SQLite for initial development.
- [x] Configure Alembic migrations.
- [x] Set up frontend-backend communication.
- [x] Create environment variable templates.
- [x] Establish the approved project folder structure.
- [x] Verify frontend and backend run successfully.

**Completion checkpoint:** Project starts successfully and frontend can communicate with backend. (COMPLETED)

## 4. Phase 2 — UI Foundation and Landing Page

- [x] Create reusable design tokens.
- [x] Implement typography and color system from DESIGN.md.
- [x] Create reusable buttons, cards, inputs and navigation components.
- [x] Build responsive landing page.
- [x] Implement hero section and CTAs.
- [x] Build product features section.
- [x] Add KNIT product preview.
- [x] Add how-it-works section.
- [x] Add Gmail integration explanation.
- [x] Add FAQ and footer.
- [x] Verify desktop, tablet and mobile layouts.

**Completion checkpoint:** Landing page visually follows the approved KNIT design system. (COMPLETED)

## 5. Phase 3 — Authentication and Application Shell

- [x] Implement registration and login.
- [x] Implement secure authentication handling.
- [x] Create authenticated application layout.
- [x] Build sidebar navigation.
- [x] Build top navigation.
- [x] Create dashboard, inbox, tasks, assistant and analytics page layouts.
- [x] Implement protected routes.
- [x] Add loading, empty and error states.

**Completion checkpoint:** Users can authenticate and navigate the application. (COMPLETED)

## 6. Phase 4 — Sample Inbox and Email Management

Start with sample email data. Real Gmail integration is not part of this phase.

- [x] Create realistic sample email dataset.
- [x] Create email database models.
- [x] Implement email listing API.
- [x] Implement email detail API.
- [x] Display emails in Smart Inbox.
- [x] Implement category navigation.
- [x] Implement email search.
- [x] Implement read/unread status.
- [x] Implement importance indicators.
- [x] Build email detail panel.
- [x] Add realistic sample emails for internship, interview, college and personal categories.
- [x] Implement read/unread and important filtering.
- [x] Implement newest/oldest sorting and pagination.
- [x] Implement soft delete, restore and confirmed permanent delete.
- [x] Enforce authenticated user ownership on every email operation.
- [x] Add backend tests for seeding, filtering, actions and ownership isolation.

**Completion checkpoint:** Users can browse, search and open sample emails. (COMPLETED)

## 7. Phase 5 — AI Email Intelligence

- [x] Configure Gemini API through the backend.
- [x] Implement email classification.
- [x] Generate email summaries.
- [x] Extract important information.
- [x] Extract company and role details when available.
- [x] Extract skills and eligibility criteria when available.
- [x] Extract application links and important dates when available.
- [x] Extract action items.
- [x] Validate AI responses using structured schemas.
- [x] Store analysis results.
- [x] Display AI analysis inside email details.
- [x] Handle missing, uncertain and failed extraction results.
- [x] Add manual category correction and regeneration.
- [x] Cache successful analysis and prevent repeated automatic calls.
- [x] Add mocked Gemini tests and missing-key handling.

**Completion checkpoint:** Sample emails can be classified, summarized and analysed accurately. (IMPLEMENTED; LIVE GEMINI VERIFICATION BLOCKED — provider HTTP 503)

## 8. Phase 6 — Tasks and Deadlines

- [x] Create task database models.
- [x] Implement task APIs.
- [x] Create tasks manually.
- [ ] Create tasks from extracted email information.
- [x] Display upcoming deadlines.
- [x] Implement task priorities.
- [x] Implement task status updates.
- [x] Allow users to mark tasks complete.
- [x] Link tasks to their source emails.

**Completion checkpoint:** Users can manage tasks and deadlines extracted from emails.

## 9. Phase 7 — AI Assistant

- [x] Create AI conversation and message models.
- [x] Build assistant chat interface.
- [x] Implement conversation history.
- [x] Implement natural-language questions about sample inbox data.
- [x] Retrieve relevant email context.
- [x] Display supporting email references.
- [x] Add suggested questions.
- [x] Validate responses against available data.
- [x] Prevent unauthorized actions.
- [x] Test common student and internship-related queries.

**Completion checkpoint:** Users can ask questions about their sample email data and receive grounded responses. (VERIFIED WITH MOCKED PROVIDER; LIVE GEMINI BLOCKED)

## 10. Phase 8 — Contextual Reply Generation

- [x] Implement authenticated reply generation endpoint.
- [x] Use server-loaded selected email context and optional cached AI analysis.
- [x] Generate relevant reply suggestions in four selectable tones.
- [x] Allow users to edit and copy generated replies.
- [x] Allow saving replies as drafts in the application, one per user/email.
- [x] Display clear generation, copy and save feedback.

Sending emails must never happen automatically.

**Completion checkpoint:** Users can generate, edit, copy and save reply drafts. (IMPLEMENTED; 50 backend tests pass, frontend build passes, provider mocked in tests; live Gemini remains blocked and browser workflow was not manually exercised.)

## 11. Phase 9 — Dashboard and Analytics

- [x] Connect dashboard to authenticated, user-owned database data.
- [x] Display active email statistics, including unread and important flag counts.
- [x] Display category distribution separately from important flags.
- [x] Display 30-day UTC email activity.
- [x] Display pending, in-progress, completed and overdue task metrics.
- [x] Display deadlines due in seven days and nearest upcoming tasks.
- [x] Display recent received emails and task updates using existing timestamps.
- [x] Display optional cached AI risk insights with an unavailable-data fallback; no live Gemini calls.
- [x] Add loading, error, zero-data and responsive analytics states.

**Completion checkpoint:** Dashboard and Analytics show user-scoped application data. (IMPLEMENTED; 56 backend tests pass, frontend production build passes, lint has only the existing AuthContext warning; UTC date handling and no-migration scope verified.)

## 12. Phase 10 — Gmail Integration

Start only after the sample-data MVP is stable and approved.

- [ ] Configure Google Cloud project.
- [ ] Configure Gmail API.
- [ ] Configure Google OAuth 2.0.
- [ ] Implement secure account connection.
- [ ] Request only necessary Gmail permissions.
- [ ] Store tokens securely on the backend.
- [ ] Retrieve authorized Gmail messages.
- [ ] Normalize Gmail messages into KNIT email models.
- [ ] Implement synchronization.
- [ ] Handle token expiration and revocation.
- [ ] Test Gmail connection and synchronization.
- [ ] Implement Gmail draft creation.
- [ ] Implement explicitly confirmed email sending only if approved.

**Completion checkpoint:** Authorized Gmail data can be securely synchronized and managed.

### Phase 10.1 — Google Cloud setup and backend OAuth configuration
- [x] Document Google Cloud project, Gmail API, consent screen and Web Application OAuth client setup.
- [x] Define the exact local callback and production callback convention.
- [x] Add backend-only OAuth client ID, client secret, redirect URI, read-only scope, encryption-key configuration and disabled-by-default integration flag.
- [x] Validate required configuration only when Gmail integration is enabled; reject non-read-only scopes and non-HTTPS redirects outside development.
- [x] Add placeholder-only OAuth values to `.env.example`.
- [ ] Complete OAuth and account connection in Phase 10.3+ (not included here).

**Phase 10.1 completion checkpoint:** Configuration and setup documentation are ready; focused config tests: 5 passed; backend suite: 61 passed. Frontend build and lint passed with existing warnings. No OAuth flow, Google request, account connection, token encryption implementation or database migration was added.

### Phase 10.2 — Connected account schema and secure token encryption
- [x] Add user-owned `ConnectedAccount` schema and provider email references with deduplication constraints.
- [x] Add Fernet authenticated token encryption using the configured backend key; fail closed on missing/invalid key or ciphertext.
- [x] Add Alembic migration `6e7f8091a2b3` and verify upgrade/downgrade on an isolated SQLite database while preserving an existing email.
- [x] Add model, encryption, uniqueness, duplicate prevention, and migration tests.
- [ ] Implement OAuth routes, token lifecycle, account UI, and Gmail sync in later approved subphases.

**Phase 10.2 completion checkpoint:** Focused model/encryption tests: 5 passed; isolated migration upgrade/downgrade: 1 passed; backend suite: 67 passed; frontend build/lint passed. No Google requests or OAuth flows were initiated.

### Phase 10.3 — Gmail OAuth connect, callback and disconnect
- [x] Add single-use, expiring, user-bound OAuth state storage and migration.
- [x] Add authenticated Gmail authorization start and safe fixed-origin callback handling with read-only scope/offline access.
- [x] Exchange callback codes server-side, retrieve Gmail profile identity, encrypt tokens and preserve an existing refresh token when omitted.
- [x] Add authenticated safe connection listing and owner-only disconnect with local credential removal and email-reference preservation.
- [x] Add minimal Connected Accounts settings UI with connect, status, return result, disconnect confirmation, loading and errors.
- [x] Add mocked OAuth tests for state, denial/provider errors, identity binding, secret-free responses, refresh-token preservation and cross-user access.
- [ ] Message listing, synchronization, content/attachment retrieval and Outlook remain out of scope (Phase 10.4+).

**Phase 10.3 completion checkpoint:** OAuth tests and migration check passed; full backend suite 73 passed; frontend build and lint passed with existing warnings. No real Google or Gmail calls were made.

### Phase 10.4 — Gmail provider and initial email sync
- [x] Add minimal provider protocol and read-only Gmail REST adapter for identity, pagination, and message detail.
- [x] Add bounded authenticated initial sync endpoint with encrypted token refresh/rotation, ownership checks, deduplication, and partial status handling.
- [x] Normalize sender/recipients/subject/body/timestamp/labels and attachment metadata without fetching attachment content.
- [x] Add database sync lease timestamp and migration `8a9b0c1d2e3f` to prevent overlapping account syncs.
- [x] Add configurable message/page caps and mocked provider tests for pagination, normalization, deduplication, ownership, refresh, error handling, partial sync and concurrency.
- [ ] Implement Gmail history cursor/incremental sync in Phase 10.5; Outlook remains out of scope.

**Phase 10.4 completion checkpoint:** Focused provider/sync and migration tests: 7 passed; full backend suite: 79 passed; frontend production build and lint passed with existing warnings. Migration revision `8a9b0c1d2e3f` was exercised on a temporary SQLite database. No live Google/Gmail calls were made.

### Phase 10.5 — Incremental Gmail history synchronization
- [x] Extend the read-only `EmailProvider` protocol and `GmailProvider` with paginated Gmail History API reads.
- [x] Persist initial history baseline and incremental page progress; advance the account cursor only after complete processing.
- [x] Import new/changed messages idempotently, preserve user-modified flags, and soft-delete provider messages reported deleted or moved to Trash.
- [x] Detect expired/invalid history cursors, mark `full_resync_required`, and reconcile stale provider-linked records only after successful bounded full resync.
- [x] Add migration `9b0c1d2e3f4a`, focused mocked history tests, and safe sync response metadata (`sync_type`, added/updated/removed, status, last successful sync).
- [x] Verify focused sync/migration tests, complete backend suite, migration head/upgrade/downgrade, frontend build and lint.

**Phase 10.5 completion checkpoint:** Focused sync/migration tests: 11 passed; full backend suite: 83 passed; Alembic head: `9b0c1d2e3f4a` and migration upgrade/downgrade test passed; frontend production build and lint passed. Existing warnings: SQLite datetime adapter deprecation, Vite large bundle, and AuthContext Fast Refresh lint warning. No live Google/Gmail requests or OAuth flows were made.

### Phase 10.6 — Gmail Settings and sync experience
- [x] Show connected account address, connection/sync status, and last successful sync time in Settings.
- [x] Add per-account Sync Now, busy/duplicate-click protection, initial/incremental count feedback, and account status refresh.
- [x] Add retry, reconnect, and explicit full-resync-required guidance using existing backend routes.
- [x] Clarify disconnect confirmation and preservation of imported KNIT emails/tasks; retain loading, empty, success, error, and responsive states.
- [x] Add zero-dependency frontend presentation tests; verify build and lint.

**Phase 10.6 completion checkpoint:** Frontend built successfully; Node built-in tests: 5 passed; Oxlint passed with the pre-existing AuthContext Fast Refresh warning. Browser interaction/responsive verification was unavailable in this environment. No backend/provider changes or live Google/Gmail requests were made.

### Phase 10.7 — Gmail security hardening and release readiness
- [x] Redact OAuth callback query parameters from Uvicorn access logs; apply no-store and no-referrer callback response headers.
- [x] Validate Fernet key format and production frontend origins when Gmail integration is enabled.
- [x] Reject the built-in or short KNIT JWT signing key outside development without changing authentication behavior.
- [x] Bound MIME parsing by depth, part count, and decoded body size; keep email bodies out of model representations.
- [x] Clean consumed/expired OAuth states and use a per-worker sync lease token for conditional heartbeat, progress, cursor, and completion updates.
- [x] Bound initial/history page requests per run and include history removals in the configured processing cap.
- [x] Add focused security tests for callback logging/headers, safe responses, lease ownership/reclaim/lost-worker behavior, configuration, MIME bounds, OAuth scope/ownership, and token-safe representations.
- [x] Verify Alembic upgrade/downgrade using the isolated SQLite migration test; run full backend suite and frontend test/build/lint.
- [x] Document deployment controls and manual production verification requirements.

**Phase 10.7 automated checkpoint (2026-11-20):** Focused security/migration tests: 41 passed. Full backend suite: 99 passed. Alembic head: `a10c3d4e5f67`; isolated upgrade/downgrade migration test passed. Frontend tests: 5 passed; production build and lint passed. Existing warnings remain (Python SQLite datetime adapter deprecation, Vite large chunk, and AuthContext Fast Refresh lint warning). Browser and real-account Google verification have not been performed; therefore production readiness is not established. No live OAuth or Google/Gmail requests were made.

## 13. Phase 11 — Testing and Final Quality

- [x] Run complete backend API and service regression suite with mocked external providers.
- [x] Run frontend tests, production build, and lint.
- [ ] Test database operations.
- [ ] Test AI classification and extraction.
- [ ] Test assistant responses.
- [ ] Test task creation and updates.
- [ ] Test reply draft workflow.
- [ ] Test authentication and authorization.
- [ ] Test security and input validation.
- [ ] Verify desktop and mobile interactions in a real browser (blocked: browser automation unavailable).
- [ ] Fix major UI and functional bugs.
- [ ] Verify all visible controls perform their intended actions.
- [x] Update project documentation with verified results and manual release checks.

**Phase 11 automated checkpoint (2026-11-20):** Backend suite 99 passed. Frontend tests 5 passed; production build and lint passed with existing warnings. Auth, email, analytics, AI/assistant/reply, tasks, OAuth, Gmail provider/sync, and migration behaviors have automated coverage, including ownership and mocked external providers. Browser navigation, live responsive behavior, and real Google account verification were unavailable and remain manual. No live Gemini/Gmail calls were made. Phase 11 automated checks are complete; production readiness is not established until manual deployment/account checks pass.

**Gemini audit rerun (2026-11-20):**
- The `google-genai` SDK is installed (3.5.0).
- The existing Gemini API key is configured locally in the backend `.env`; it was not printed or copied to frontend code.
- `gemini-3.8-flash` was listed as available but live generation returned HTTP 503.
- After explicit user approval, the configuration was changed to `gemini-3.5-flash`, and a direct live comparison had successfully verified `gemini-3.5-flash`.
- Subsequent backend pings through the application returned HTTP 504 timeout twice; live Gemini verification remains BLOCKED and no live success is reported.
- At the time of this earlier audit, Gmail OAuth credentials and encryption configuration were not present in the backend `.env`; see the secure environment setup audit below for the later local key setup. Real Gmail authorization and synchronization remain blocked pending user credentials and explicit consent.
- Automated rerun: backend suite 99 passed in a project-local temp directory. Frontend tests 5 passed, build passed, lint passed with one existing Fast Refresh warning.
- Backend health endpoint returned `{"status":"ok"}` successfully on a temporary local port.

## 14. Agent Execution Protocol

For every assigned task, the AI agent must:

1. Read the relevant project documentation.
2. Inspect existing code before modifying anything.
3. Explain the intended implementation briefly.
4. Implement only the assigned task.
5. Run relevant tests and checks.
6. Fix errors introduced by its changes.
7. Report modified files.
8. Report completed and pending tasks.
9. Mention any blockers honestly.
10. Wait for approval before starting the next major phase.

## 15. Progress Tracking

Maintain task status using:

- NOT STARTED
- IN PROGRESS
- BLOCKED
- COMPLETED

Update this document whenever a task is completed.

Never mark a task completed without verifying its implementation.

## Final Development Principle

Build KNIT as a reliable, secure and useful product.

Start with a working sample-data MVP. Add real Gmail integration only after the core product is stable.

**Understand first. Plan second. Implement incrementally. Test continuously.**

**Phase 9 audit (2026-11-19):** Backend suite rerun with `DEBUG=true` scoped to the test subprocess: 56 passed. The default process environment contained invalid `DEBUG=release`; no project environment or `.env` file was changed. Frontend production build passed (Vite reports the existing >500 kB main chunk warning); lint passed with the existing `AuthContext.tsx` Fast Refresh warning. Authenticated API behavior is covered by TestClient tests (200 for owner and other authenticated users, 401 unauthenticated) with isolation, deleted email, UTC boundaries, task deadlines and empty data assertions. Browser-only runtime and viewport verification remain unperformed.

**Final audit rerun (2026-11-19):** Backend: 56 passed with `DEBUG=true` scoped to the pytest process; pytest reported a cache write permission warning. Frontend production build passed with the existing large-chunk warning. Lint passed with the existing `AuthContext.tsx` Fast Refresh warning. No implementation defects were identified and no application code changes were made. Browser-only responsive/runtime behavior remains unverified.

### Secure environment setup audit (2026-11-20)
- **COMPLETED:** Confirmed canonical settings for JWT, Fernet, database, CORS, Gemini, and Gmail. `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `TOKEN_ENCRYPTION_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GMAIL_REDIRECT_URI`, and `ALLOWED_ORIGINS` were subsequently added as backward-compatible aliases. `FRONTEND_URL` is supported for callback routing/CORS; `SQLITE_DB_PATH` remains intentionally unused.
- **COMPLETED:** Generated and locally stored a high-entropy JWT signing secret and a Fernet-compatible Gmail token key in the ignored backend `.env`, without printing either value. No `connected_accounts` table/token rows existed before key generation.
- **COMPLETED:** Confirmed the configured relative SQLite URL resolves to `backend/knit.db`, and explicitly set the same URL without changing the existing database path.
- **COMPLETED:** Verified the Gmail callback route and read-only scope; integration remains disabled.
- **COMPLETED:** Updated both environment example files to use actual setting names and blank secret placeholders, not fake OAuth/Fernet values.
- **COMPLETED:** Focused configuration/encryption tests passed (13 passed); runtime JWT sign/verify, Fernet compatibility, database path, and read-only scope validation passed.
- **NOTE:** Rotating the JWT signing secret invalidates previously issued browser/API JWTs; users may need to sign in again. Database records were not modified.
- **PENDING USER ACTION:** Enter Google OAuth client ID and client secret into secure local environment storage using the implementation's actual names. Do not share either value in chat.
- **PENDING USER ACTION:** Gemini key was already configured and preserved; do not replace it unless deliberately rotating it.
- **BLOCKED:** Real Gemini/Gmail calls were not made in this setup pass; Google authorization has not been initiated.

### Browser smoke test (2026-11-20)
- **VERIFIED:** Frontend/backend started together against an isolated, migrated SQLite test database. Registration and dashboard load succeeded. `/app`, `/app/inbox`, `/app/tasks`, `/app/assistant`, `/app/analytics`, and `/app/settings` returned HTTP 200 and rendered their expected page headings.
- **PARTIALLY VERIFIED:** Inbox category navigation to Internship worked; a sample email detail opened; read/unread and important toggles worked and were restored to their original state. Settings showed Gmail disconnected; no OAuth flow was started.
- **BLOCKED / NOT VERIFIED:** Search, status/sort/pagination result correctness, task CRUD, assistant message submission, reply generation/save, analytics values, login/logout, desktop/mobile viewport behavior, and live Gmail connect/sync were not fully exercised.
- **ISSUE / UNCERTAINTY:** During detail inspection, the browser showed a Gemini-temporarily-unavailable message and an HTTP 502 resource error; a reply draft UI state also changed unexpectedly. No explicit AI-analysis or reply-generation action was intentionally selected, so the origin of those requests/state changes was not confirmed. No further AI/Gmail actions were attempted.
- Both servers were stopped and only the isolated browser-test database was removed. The existing user database and local environment configuration were not changed.
- Production readiness remains unverified; complete the remaining browser checks and approved real-provider verification before making that claim.

### Environment input panel compatibility (2026-11-20)
- **COMPLETED:** Added backward-compatible `AliasChoices` for AI Studio panel names while retaining existing application setting names.
- **COMPLETED:** `FRONTEND_URL` now validates as an HTTP(S) origin, is added to CORS origins, and takes precedence for the fixed OAuth callback return origin.
- **COMPLETED:** Kept `SQLITE_DB_PATH` unrecognized so it cannot silently select a different database from `DATABASE_URL`.
- **VERIFIED:** Focused config/OAuth tests: 23 passed. Full backend suite: 104 passed; five existing SQLite datetime adapter deprecation warnings remain.
- **PENDING USER ACTION:** Provide Google OAuth client ID and secret through secure environment fields. Do not send credentials in chat.
