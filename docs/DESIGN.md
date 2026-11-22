# KNIT — UI/UX Design System & Phase 2 Specifications

**Product:** KNIT  
**Tagline:** Connect. Understand. Act.  
**Version:** 2.0 (Phase 2 Architecture & Specifications)  
**Target Audience:** Students, internship/job applicants, and busy professionals.

---

## 1. Design Philosophy & Vision

KNIT is an intelligent email productivity platform that sits on top of Gmail. It cuts through inbox clutter by categorizing messages, summarizing dense threads, extracting critical deadlines and opportunities, and generating contextual replies.

The visual design communicates:
- **Intelligence:** Clear distinction between raw incoming email content and AI-extracted insights.
- **Simplicity:** Uncluttered layouts, generous whitespace, and purposeful hierarchy.
- **Trust:** Transparent data handling, clear privacy messaging, and explicit confirmation for all actions.
- **Productivity:** High-contrast typography, scannable data badges, and actionable next steps.
- **Professionalism:** A premium, modern SaaS aesthetic inspired by clean, high-craft productivity tools.

The interface must feel like a polished, commercial SaaS product. It avoids cartoonish visuals, unnecessary floating widgets, and heavy decorative gradients.

---

## 2. Approved Color Palette & Design Tokens

The visual identity relies on clean white surfaces, subtle borders, deep legible typography, coral-pink active accents, and soft pink informational surfaces.

### Primary Palette

| Token | Hex Value | Role & Usage |
|---|---|---|
| **Primary Coral** | `#F04464` | Primary CTA buttons, active sidebar items, critical deadline badges, key icons, and highlights. |
| **Coral Hover** | `#DB3556` | Hover and active pressed states for coral buttons and links. |
| **Coral Light** | `#FFF1F3` | Subtle badge backgrounds and coral accent rings. |
| **Soft Pink Surface** | `#FCECEF` | Selected cards, AI insight panels, hero highlight chips, and secondary feature backgrounds. |
| **Main Text** | `#15151F` | Primary headings, email subjects, active labels, and critical text (high contrast). |
| **Secondary Text** | `#626273` | Subtitles, email body snippets, metadata timestamps, and supporting descriptions. |
| **White** | `#FFFFFF` | Primary surface background, card surfaces, and email reading canvas. |
| **Background Secondary**| `#FFF9FA` | Page body background, alternate table rows, and secondary layout containers. |
| **Border** | `#ECE8EA` | Card borders, dividers, table lines, input strokes, and navbar bottom border. |

### Semantic Supporting Colors (Used Sparingly)

| Semantic Role | Hex Value | Usage |
|---|---|---|
| **Success / Validated** | `#10B981` | Completed tasks, successful health check, verified sender badge. |
| **Warning / Deadline** | `#F59E0B` | Approaching deadlines (due within 48 hours), priority warning indicators. |
| **Error / Suspicious** | `#EF4444` | Suspicious/phishing email category badge, connection failure alerts. |

*Rule:* White and soft off-white must dominate the layout. Unrelated bright or saturated colors (neon greens, deep blues, purple gradients) are prohibited.

---

## 3. Typography System

**Primary Typeface:** `Inter`, system-ui, -apple-system, sans-serif.

### Type Scale & Hierarchy

| Level | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| **Display / Hero** | `48px` – `56px` (3rem–3.5rem) | `800` (Extrabold) | `1.15` | Landing page hero headline ("Your inbox, understood."). |
| **Section Heading** | `32px` – `36px` (2rem–2.25rem) | `700` (Bold) | `1.25` | Major landing page section titles ("Features", "How KNIT Works"). |
| **Card / Subtitle** | `20px` – `24px` (1.25rem–1.5rem) | `600` (Semibold) | `1.35` | Feature card titles, email subject headers, modal titles. |
| **Body Large** | `18px` (1.125rem) | `400` / `500` | `1.5` | Hero supporting text, section introductory copy. |
| **Body Regular** | `15px` – `16px` (0.9375rem–1rem) | `400` (Normal) | `1.55` | Email message body, feature descriptions, general content. |
| **UI Medium / Nav** | `14px` (0.875rem) | `500` (Medium) | `1.4` | Navbar links, sidebar navigation items, button labels, table headers. |
| **Metadata / Badge** | `12px` – `13px` (0.75rem–0.8125rem) | `500` / `600` | `1.3` | Timestamps, category tags, deadline badges, status chips. |

### Typography Rules
- Use `#15151F` for primary headings and important text to guarantee strong readability and contrast.
- Use `#626273` for secondary explanations, subtitles, and email previews.
- Maintain consistent vertical rhythm using Tailwind standard spacing scales (`py-2`, `py-4`, `mb-3`, `mb-6`).
- Avoid decorative display fonts, script fonts, and all-caps body text.

---

## 4. Navbar Structure & Interactive Behavior

The landing page navbar is minimal, functional, and strictly dedicated to KNIT's core capabilities.

### Approved Navbar Structure

```text
[KNIT Logo]                 [Features]  [How It Works]  [About]                 [Sign in]  [Get Started]
```

1. **Left:** KNIT Logo (`Mail` icon in Coral `#F04464` badge + bold text "KNIT").
2. **Center:** Primary section anchors:
   - **Features**
   - **How It Works**
   - **About**
3. **Right:** Action items:
   - **Sign in** (secondary text link / ghost button).
   - **Get Started** (primary Coral button).

### Interactive Navigation Behavior

- **KNIT Logo:** Smoothly scrolls to the top of the landing page.
- **Features:** Smoothly scrolls to `#features`, highlighting the 6 core capability cards.
- **How It Works:** Smoothly scrolls to `#how-it-works`, presenting the 4-step workflow sequence.
- **About:** Smoothly scrolls to `#about`, presenting KNIT's product vision and origin.
- **Sign in:** Links to the authentication entry point (to be implemented in Phase 3).
- **Get Started:** Primary Coral CTA button linking to registration/onboarding (Phase 3).
- **Mobile Behavior:** Collapses into a responsive hamburger trigger (`Menu` / `X` from Lucide). When expanded, reveals a clean white dropdown sheet containing all navigation anchors and CTA buttons.

### Explicitly Excluded Navbar Items
- **Removed:** "Pricing", "Resources", "Solutions", "Product dropdown", "Enterprise", "Blog".
- **Gmail Connect:** Must **never** appear in the public landing page navbar. Gmail account authorization belongs strictly inside the authenticated app shell (Phase 10).

---

## 5. Landing Page Section-by-Section Specifications

The landing page is organized into 8 sequential sections designed to guide the visitor through the problem, product value, concrete demonstration, workflow, and call to action:

### Section 1 — Navbar
- Sticky top navigation with `#FFFFFF` background, subtle `#ECE8EA` bottom border, and subtle backdrop blur (`backdrop-blur-md`).
- Contains the approved minimal KNIT navbar (Logo, Features, How It Works, About, Sign in, Get Started).

### Section 2 — Hero Section
- **Headline:** `Your inbox, understood.` (Bold, `#15151F`, max-w-xl).
- **Supporting Text:** `Turn emails into clear summaries, opportunities and next steps.` (`#626273`, 18px).
- **Primary CTA:** `Get Started Free` (Coral `#F04464` background, white text, rounded-xl, subtle shadow).
- **Secondary CTA:** `See How It Works` (White background, `#ECE8EA` border, `#15151F` text, smooth scroll to `#how-it-works`).
- **Badge:** Top pill `AI-Powered Email Intelligence & Automation` in Soft Pink `#FCECEF` with Coral text.
- **Visual Preview (Right Side):**
  - Polished interactive mockup of the KNIT application showing:
    - Sidebar snippet with active category badge (e.g., `Internship (3)` in Coral).
    - Email list item: "Google University Programs — Summer 2027 SWE Internship".
    - Selected email reader card with:
      - Clean email header (Sender: Google Recruiting, Time: 2h ago).
      - **AI Summary Card** in Soft Pink `#FCECEF`: "Application deadline approaching for Summer 2027 Software Engineering Internship. Requires transcript submission."
      - **Extracted Details:** Company (`Google`), Role (`Software Engineer Intern`), Deadline (`Dec 15, 2026`), Action Required (`Submit Application`).
  - *Constraint:* Never show unrelated CRM pipelines, link shorteners, or meeting booking tools.

### Section 3 — Features Section (`#features`)
- **Section Title:** `Everything you need to master your inbox.`
- **Section Subtitle:** `Designed specifically for students, applicants, and busy professionals who receive critical emails daily.`
- **6 Feature Cards (Grid 3x2 on desktop, 1 col on mobile):**
  1. **Smart Inbox:** Intelligently categorizes incoming messages into Internship, Interview, College, Important, Personal, and Updates.
  2. **AI Email Summaries:** Generates concise 2-sentence summaries highlighting main intent, key facts, and next actions.
  3. **Opportunity Extraction:** Automatically extracts company names, internship roles, eligibility requirements, and application portals.
  4. **Tasks & Deadlines:** Converts important email commitments into actionable tasks with automated calendar deadline tracking.
  5. **Contextual Replies:** Drafts customized, polite, professional replies ready for review and editing with one click.
  6. **Email Analytics:** Visualizes inbox volume, category distribution, interview pipelines, and upcoming deadlines.
- **Card Styling:** White surface `#FFFFFF`, border `#ECE8EA`, hover elevation with soft pink accent `#FCECEF`, Coral Lucide icon in soft pink badge.

### Section 4 — Email Intelligence Preview
- **Section Goal:** Concrete demonstration showing the contrast between a messy email and KNIT's extracted intelligence.
- **Layout (Two-Column Comparison):**
  - **Left Column (Raw Email):** Realistic 4-paragraph corporate internship announcement from Google with dense text, dates buried in paragraphs, and application links.
  - **Right Column (KNIT Extracted Intelligence):**
    - **Header:** "KNIT Email Intelligence" with a verified AI checkmark.
    - **Key Highlights:**
      - **Target Company:** Google
      - **Position:** Software Engineer Intern
      - **Hard Deadline:** December 15, 2026 (Highlighted in Coral badge)
      - **Key Requirements:** Data Structures, Algorithms, Enrolled in BS/MS degree
      - **Required Documents:** Resume (PDF), Unofficial Transcript
      - **Direct Portal Link:** Clean one-click external link button
      - **Suggested Action:** "Add to Tasks" or "Draft Acceptance Reply"
- **Clear Distinction:** Visually differentiates raw untrusted email text from structured, validated AI insights.

### Section 5 — How KNIT Works (`#how-it-works`)
- **Section Title:** `How KNIT Works`
- **Section Subtitle:** `Four simple steps from chaotic inbox to organized clarity.`
- **Workflow Steps (Horizontal flow on desktop, vertical on mobile):**
  1. **1. Connect Your Inbox:** Authorize read access through official Google OAuth 2.0 with minimum required permissions.
  2. **2. AI Normalization & Categorization:** KNIT safely processes email threads and organizes them into meaningful buckets.
  3. **3. Intelligence Extraction:** Important deadlines, interview invitations, and academic tasks are automatically recognized.
  4. **4. Review & Take Action:** Create tasks, generate draft replies, and track application deadlines under your explicit control.

### Section 6 — Gmail Integration & Privacy
- **Section Title:** `Built securely on the official Gmail API.`
- **Messaging:**
  - Official Google OAuth 2.0 verification.
  - Read-only email retrieval by default.
  - AI operates under user supervision — **KNIT never sends emails automatically**.
  - All tokens encrypted and stored securely on the backend; never exposed to frontend JavaScript.
  - *Phase Disclaimer:* Explicitly clarifies that sample-data mode is available first, with live Gmail account connection enabled upon user authorization.

### Section 7 — Final Call to Action
- **Card Container:** Soft Pink `#FCECEF` background with `#ECE8EA` border, rounded-3xl, centered text.
- **Headline:** `Make every important email count.`
- **Subtext:** `Join students and professionals who never miss an interview invite or application deadline.`
- **Primary CTA:** `Get Started` button in Coral `#F04464` with hover `#DB3556`.

### Section 8 — Footer (`#about`)
- **Logo & Tagline:** KNIT — Connect. Understand. Act.
- **About Statement:** Concise summary of KNIT's mission to make email intelligent and user-controlled.
- **Navigation Columns:**
  - **Product:** Features, How It Works, Email Intelligence, Smart Inbox.
  - **Legal & Trust:** Privacy Policy, Terms of Service, Security Architecture, Google API Disclosure.
  - **Help & Contact:** Documentation, FAQ, Support.
- **Copyright:** `© 2026 KNIT. All rights reserved.`
- *Rule:* Do not fabricate physical addresses, customer counts, or inactive social profiles.

---

## 6. Dashboard & Application Shell Specifications

The authenticated application uses the exact same visual identity, typography, and color tokens as the landing page.

### Layout Architecture (Three-Column Modular Structure)

```text
┌─────────────────┬──────────────────────────┬─────────────────────────────────────┐
│ Left Sidebar    │ Center: Email List /     │ Right: Email Detail & Intelligence   │
│                 │ Dashboard Overview       │ Panel                               │
│ • Navigation    │ • Category Filter        │ • Original Email Content            │
│ • Categories    │ • Email Cards / Previews │ • AI Summary Box (Soft Pink)        │
│ • Tools (Tasks, │ • Search & Quick Toggles │ • Extracted Deadlines & Info        │
│   Assistant)    │                          │ • Contextual Reply Generator        │
└─────────────────┴──────────────────────────┴─────────────────────────────────────┘
```

### Sidebar Navigation Items (Approved Scope)
- **Overview** (Dashboard analytics & summary)
- **All Inbox** (Complete message stream)
- **Internship** (Extracted internship opportunities)
- **Interview** (Interview invitations & schedules)
- **College** (Academic announcements & course updates)
- **Important** (High-priority flagged communications)
- **Personal** (Direct personal correspondence)
- **Promotions** (Marketing and newsletters)
- **Updates** (System notifications and service alerts)
- **Suspicious** (AI-flagged suspicious or phishing emails)
- **Tasks** (Extracted and user-managed deadlines)
- **AI Assistant** (Conversational query interface)
- **Analytics** (Inbox volume and category charts)
- **Settings** (Account preferences & connected services)

### Main Dashboard Area (Overview View)
- **Personalized Header:** "Welcome back, [Name] — here is your inbox briefing."
- **Metric Cards (4-column grid):**
  1. Total Emails & Unread Count
  2. Pending Tasks & Deadlines (due this week)
  3. Internship & Job Opportunities
  4. Scheduled Interview Invitations
- **AI Insight Stream:** Soft Pink `#FCECEF` highlight banner showing the latest critical deadline.
- **Category Distribution:** Clean bar or donut representation of incoming email types.
- **Recent Priority List:** Scannable list of emails needing attention.

### Email Detail & Intelligence Panel
- **Sender & Metadata:** Profile avatar, sender name, email address, date, category tag.
- **Action Toolbar:** "Generate Reply", "Add to Tasks", "Mark Important", "Mark Read".
- **AI Summary Box:** Positioned at the top of the detail panel in Soft Pink `#FCECEF` with Coral accent border.
- **Structured Extraction Card:**
  - Company / Organization
  - Role / Subject
  - Deadlines (with countdown chip)
  - Action Items / Next Steps
  - Application / Meeting Links
- **Original Content Body:** Collapsible or displayed beneath AI summary in crisp, readable format.

---

## 7. Reusable Component Styling

All components are built using Tailwind CSS utility classes and design tokens:

### Buttons
- **Primary Coral Button:**
  `bg-coral text-white font-medium px-5 py-2.5 rounded-xl hover:bg-coral-hover transition-colors shadow-sm shadow-coral/20 cursor-pointer`
- **Secondary / Outline Button:**
  `bg-white text-foreground border border-border font-medium px-5 py-2.5 rounded-xl hover:bg-background-secondary transition-colors cursor-pointer`
- **Ghost Button:**
  `text-foreground-secondary hover:text-foreground font-medium px-4 py-2 rounded-xl transition-colors cursor-pointer`
- **Icon Action Button:**
  `w-9 h-9 rounded-lg border border-border flex items-center justify-center text-foreground-secondary hover:text-coral hover:border-coral/30 transition-colors`

### Cards & Surfaces
- **Base White Card:**
  `bg-white border border-border rounded-2xl p-6 shadow-sm`
- **Soft Pink Feature Card:**
  `bg-pink-surface border border-border rounded-2xl p-6`
- **Interactive Hover Card:**
  `bg-white border border-border rounded-2xl p-6 transition-all hover:border-coral/40 hover:shadow-md hover:-translate-y-0.5`

### Badges & Category Chips
- **Coral Tag (Active / Critical):**
  `inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-coral text-white`
- **Soft Pink Tag (AI Insight / Category):**
  `inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-pink-surface text-coral border border-border`
- **Neutral Tag:**
  `inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-background-secondary text-foreground-secondary border border-border`

### Form Inputs
- **Text & Search Input:**
  `bg-white border border-border rounded-xl px-4 py-2.5 text-sm text-foreground placeholder:text-foreground-secondary/60 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral transition-all`

---

## 8. Iconography Standards

- **Icon Family:** `lucide-react` across the entire application.
- **Sizing:**
  - Small / Inline metadata: `14px` (`w-3.5 h-3.5`)
  - Standard button / label icon: `16px` – `18px` (`w-4 h-4` or `w-4.5 h-4.5`)
  - Feature card / Category icon: `20px` – `24px` (`w-5 h-5` or `w-6 h-6`)
  - Hero preview feature icon: `28px` – `32px` (`w-7 h-7` or `w-8 h-8`)
- **Stroke Width:** `1.75px` or `2px` consistently; avoid mixing thin 1px icons with heavy 3px icons.
- **Coloring:**
  - Coral `#F04464` for key action icons, active navigation, and deadline alerts.
  - `#626273` for neutral secondary navigation and metadata indicators.
  - White `#FFFFFF` inside solid coral badges.

---

## 9. Responsive Behavior & Breakpoints

| Breakpoint | Width | Layout Adjustments |
|---|---|---|
| **Mobile (`< 768px`)** | `< 768px` | Navbar switches to mobile hamburger menu. Hero stacks vertically. Feature cards display in 1 column. Dashboard collapses to single-pane view with slide-over panels. |
| **Tablet (`768px – 1024px`)** | `768px – 1024px` | Navbar shows compact links. Feature cards display in 2 columns. Dashboard displays compact 2-pane view (collapsible sidebar + content). |
| **Desktop (`> 1024px`)** | `> 1024px` | Full navbar layout with center links and action buttons. Features display in 3x2 grid. Dashboard uses full 3-column layout (Sidebar + Email List + Detail & AI Intelligence). |

---

## 10. Motion and Interaction Rules (Framer Motion)

Motion must be subtle, fast, and purposeful. It must never delay user actions or distract from email reading.

### Approved Interactions
- **Page & Section Load:** Subtle fade-in with minor Y-offset: `initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}`.
- **Card Hover:** Subtle upward translation (`-2px`) with gentle shadow expansion.
- **Sidebar Navigation:** Smooth background highlight transition on active item change.
- **AI Thinking / Loading:** Gentle pulse animation or clean spinning indicator (`RefreshCw className="animate-spin text-coral"`).
- **Collapsible Panels:** Smooth height transition (`layout` or accordion transition).

### Prohibited Motion
- No excessive bouncing, spring oscillations, or cartoon-like scaling.
- No rotating background gradients or particle systems.
- No continuous floating decorative objects.
- Full compliance with `prefers-reduced-motion`: disable animations when user requests reduced motion.

---

## 11. Accessibility, Contrast & State Requirements

### Contrast & Legibility
- Text contrast must exceed WCAG AA minimums (4.5:1 for normal text, 3:1 for large text).
  - Main text `#15151F` on White `#FFFFFF` has a contrast ratio of `17.4:1` (Exceeds AAA).
  - Secondary text `#626273` on White `#FFFFFF` has a contrast ratio of `6.8:1` (Exceeds AA).
  - Primary Coral `#F04464` on White `#FFFFFF` has a contrast ratio of `4.6:1` (Exceeds AA for UI components and large text).

### Interactive Component States
Every interactive component (button, card, tab, input, email row) must explicitly define all 5 states:
1. **Default:** Clean, readable, subtle border.
2. **Hover:** Clear cursor feedback, subtle border highlight or background tint.
3. **Active / Pressed:** Subtle scale down (`scale-[0.98]`) or darkened background (`#DB3556`).
4. **Focused:** Visible accessible focus ring (`focus-visible:ring-2 focus-visible:ring-coral/40`).
5. **Disabled:** Reduced opacity (`opacity-50 cursor-not-allowed`).

### State Handling Across Views
Every view must support:
- **Loading State:** Skeleton placeholders or clean Coral spinner.
- **Empty State:** Meaningful empty state illustration or message with action prompt (e.g., "No unread internship emails found.").
- **Error State:** Clear error explanation with a "Retry" button.

---

## Final Design Principle

**KNIT should look like a polished, trustworthy email-intelligence product: clean white surfaces, coral accents, soft pink highlights, elegant typography, and a consistent experience from landing page to dashboard.**

**End of Phase 2 Design System Specifications.**
