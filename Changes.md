# OMA WebUI — Change Log

Base: OpenWebUI v0.11.0  
Branch: `v0.11.0`  
Client: Enerparc / OMA (O&M AI Agent)

---

## Phase 1 — Enerparc Branded Login Page

**Commit:** `d11109de6`

**What changed:**
- `src/routes/auth/+page.svelte` — full custom login page: Enerparc logo, solar farm background carousel, "Continue with Microsoft" Azure AD SSO, tool selector dropdown, "Secured by Azure AD · Enerparc AG" footer
- `static/oma-login-bg.png` — login background image
- `vite.config.ts` — dev proxy config to point to local backend

---

## Phase 2 — Core Invertix Agent UI (v0.10.2 → v0.11.0 Migration)

**Commits:** `8d65f82a1` → `ebac20919`

### New components
| File | Purpose |
|---|---|
| `src/lib/components/chat/InvertixStepsCard.svelte` | Reasoning steps card — shows agent tool calls, "Thinking..." spinner on init, collapses when done |
| `src/lib/components/chat/InvertixDocCard.svelte` | Document download card shown below agent messages when a report is generated |
| `src/lib/components/chat/InvertixChartCard.svelte` | Inline Chart.js chart card rendered from `INVERTIX-CHART` SSE events |
| `src/lib/components/chat/Messages/EmojiRatingPopup.svelte` | Custom emoji feedback popup (replaces OpenWebUI default rating modal) |
| `src/lib/components/common/ThemeSwitcher.svelte` | Light/dark toggle in the navbar |
| `src/lib/stores/emojiPopup.ts` | Global store — lets ResponseMessage open the popup while Chat.svelte renders it at root level |
| `src/lib/stores/chartLib.ts` | Chart.js bundle loader (lazy, cached) |

### Modified files
| File | What changed |
|---|---|
| `src/lib/components/chat/Messages/ResponseMessage.svelte` | InvertixStepsCard placed above content; Skeleton suppressed; `responding` prop fixed; default rating modal disabled; EmojiRatingPopup wired; InvertixDocCard uses `docs={array}` prop; single download toolbar button with localStorage persistence |
| `src/lib/components/chat/Chat.svelte` | EmojiRatingPopup mounted at root; `inv_rid_*` / `inv_backend_*` / `inv_dl_*` localStorage keys written from SSE events; chart filter event handler |
| `src/lib/components/layout/Sidebar.svelte` | Artifacts panel moved above Chats section; switched from `Folder` to `SidebarSection` component (chevron right, hover-only, matches Chats style); Enerparc full logo in sidebar header |
| `src/lib/components/chat/Navbar.svelte` | Removed unused `showArchivedChats` import (not exported in v0.11.0); ThemeSwitcher added |
| `src/app.html` | Title set to `O&M Agent`; splash screen wired to `static/splash.png` / `static/splash-dark.png` |
| `src/lib/constants.ts` | `INVERTIX_BACKEND` default URL set to Enerparc Railway backend |
| `src/routes/+layout.svelte` | Model icon set to `static/favicon.png`; chart filter script injected |

---

## Phase 3 — OMA Brand Assets

**Commit:** `1a49e9bc5`

All brand files replaced in `static/`. Drop-in replacements — filenames kept identical so no code changes needed.

| File | Dimensions | Used for |
|---|---|---|
| `static/favicon.svg` | 1042×1042 viewBox | Browser tab icon (SVG) |
| `static/favicon.png` | 512×512 | Browser tab icon + model avatar in chat |
| `static/favicon.ico` | 32×32 | Legacy browser icon |
| `static/favicon-96x96.png` | 96×96 | Android/Chrome icon |
| `static/apple-touch-icon.png` | 180×180 | iOS home screen icon |
| `static/web-app-manifest-192x192.png` | 192×192 | PWA manifest icon |
| `static/web-app-manifest-512x512.png` | 512×512 | PWA manifest icon |
| `static/splash.png` | 500×500 transparent | Loading screen — light mode |
| `static/splash-dark.png` | 500×500 transparent | Loading screen — dark mode |
| `static/logo.png` | 500×500 | "Her" theme variant logo |
| `static/enerparc-full-logo.png` | — | Expanded sidebar logo + login header — **Enerparc, intentionally kept** |

**Sidebar behaviour:**
- Expanded → `enerparc-full-logo.png` (Enerparc horizontal logo)
- Collapsed → `favicon.png` at 20px (OMA icon, already wired in `Sidebar.svelte:962`)

---

## Phase 4 — Feedback Pills + Langfuse `feedback_categories` Score

**Commit:** *(this phase — see below)*

### What changed

**`src/lib/components/chat/Messages/EmojiRatingPopup.svelte`**
- Added 5 O&M-specific feedback category pills above the textarea (multi-select):
  - Wrong Data · Wrong Time Period · Wrong Plant / Site · Incomplete Answer · Not Helpful
- Active pill style: `#003877` (Enerparc dark blue) background, white text
- Inactive pill style: zinc border, hover → `#73B2F2` (Enerparc light blue)
- Textarea reduced from `rows=3` to `rows=2`
- `onSubmit` callback extended: `{ rating, feedback, reasons: string[] }`

**`src/lib/stores/emojiPopup.ts`**
- `EmojiPopupState.onSubmit` type updated to include `reasons: string[]`

**`src/lib/components/chat/Messages/ResponseMessage.svelte`**
- Both thumbs-up and thumbs-down `emojiPopup.open` handlers updated:
  - `fullComment` = `"<pills joined> — <free text>"` (pills prepended to comment)
  - `sendFeedback('feedback_categories', 1, reasons.join(', '))` sent when pills selected
  - Fires alongside existing `user_feedback_detail` score

**`backend/app/routes_openai_compat.py`** *(invertix-multitenant-agent repo)*
- `feedback_categories` added to `_VALID_SIGNALS` allowlist

**`backend/app/routes_analytics.py`** *(invertix-multitenant-agent repo)*
- `feedback_categories` added to `_SIGNALS` analytics list

### Langfuse scores per feedback submission
| Score name | Value | Comment |
|---|---|---|
| `user_feedback` | +1 / -1 | — |
| `user_feedback_detail` | 1–4 (emoji) | `"Wrong Data, Wrong Time Period — optional text"` |
| `feedback_categories` | 1 | `"Wrong Data, Wrong Time Period"` |

---

## Phase 5 — Weekly Survey Widget

**Commit:** *(this phase)*

Periodic, bottom-right feedback card. Appears after 8 s on first load (≥7 days since last completion, ≥3 days since snooze). Fixed `320×400 px` shell — content slides inside; card never resizes between stages.

### Stages
| Stage | Description |
|---|---|
| **Invite** | Full-bleed background image + dark-blue gradient overlay. Headline, "Take a Survey" CTA, "Remind me later" snooze |
| **Questions** | White card, animated progress dots, four questions in sequence |
| **Thank you** | Personalised with first name (`$user?.name`), auto-dismisses after 2.8 s |

### Question types implemented
| Type | Description |
|---|---|
| `stars` | 5-star tap row with hover highlight, stored as 1–5 |
| `choice` | Single-select radio-style buttons |
| `slider` | Range input with gradient fill track, large numeric readout, min/max labels |
| `text` | Free-text textarea, skippable |

### New files
| File | Purpose |
|---|---|
| `src/lib/components/chat/WeeklySurvey.svelte` | Full widget — invite → questions → thank you stages, all question types, localStorage scheduling |

### Modified files
| File | What changed |
|---|---|
| `src/routes/+layout.svelte` | `WeeklySurvey` imported and mounted just before `<Toaster>` |

### LocalStorage keys
| Key | Set when |
|---|---|
| `inv_survey_last_shown` | Widget shown (on `onMount` timer fire) |
| `inv_survey_last_completed` | User submits all questions |
| `inv_survey_dismissed_at` | User clicks "Remind me later" |

### Design details
- Background rotates between `/oma-login-bg-01.png` and `/oma-login-bg-03.png` (bg-02 excluded — too light, text illegible)
- Gradient overlay: `rgba(0,56,119,0.25) → rgba(0,56,119,0.92)` bottom-weighted
- Brand colours: `#003877` (Enerparc dark blue) throughout; slider thumb, stars, progress dots, CTA button
- Question transitions: `fly` with directional `x` offset, clipped inside a `relative overflow-hidden` wrapper so old + new questions don't stack

### Pending (next sprint)
- Wire answers to `/v1/survey` backend endpoint with `userId` from JWT
- Persist responses in new `survey_responses` table (S3-backed or Postgres)
- Revert `SHOW_DELAY_MS` from `2000` → `8000` before production deploy
