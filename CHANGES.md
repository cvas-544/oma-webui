# OpenWebUI Fork — Change Log

**Forked from:** OpenWebUI `v0.10.2` (commit `ecd48e2`)
**Fork purpose:** Invertix / O&M Agent — multi-tenant AI agent UI for solar plant operations.

When forking for a new deployment, apply every change listed here to the new upstream base.
New files can be copied verbatim; modified files need the diff applied on top of the upstream version.

---

## New Files (copy verbatim)

| File | Purpose |
|------|---------|
| `src/lib/components/chat/InvertixQuickDetails.svelte` | Grouped option picker card rendered above the input field; driven by `invertix:ask_options` event from the stream filter. Lets users click an option instead of typing. |
| `src/lib/components/chat/InvertixDocCard.svelte` | Download card for agent-produced documents (PDF / Excel); rendered when filter emits `invertix:doc_ready`. |
| `src/lib/components/chat/InvertixStepsCard.svelte` | Thinking / tool-call step timeline card; rendered from `invertix:step` events. |
| `src/lib/components/chat/Messages/EmojiRatingPopup.svelte` | Emoji-based explicit feedback popup (4 emojis: Terrible / Bad / Okay / Amazing). Appears above the input field when thumbs up/down is clicked. Uses Enerparc colour palette. State is managed via the global `emojiPopup` store so the popup renders at the Chat root level, outside any transform/opacity stacking context. |
| `src/lib/components/layout/Sidebar/ArtifactsPanel.svelte` | Sidebar panel listing all generated artifacts (charts, PDFs, Excel) for the current session. |
| `src/lib/stores/artifacts.ts` | Writable Svelte store that accumulates artifact metadata emitted during a run. Persisted to `localStorage` so the list survives page reload. |
| `src/lib/stores/emojiPopup.ts` | Global writable store for `EmojiRatingPopup` open/close state. Allows `ResponseMessage` to open the popup while `Chat.svelte` renders it at the root level. |
| `static/enerparc-full-logo.png` | Full Enerparc logo used in the sidebar header. Replace with the client logo for each deployment. |
| `static/enerparc-logo.png` | Compact Enerparc logo (icon only). |

---

## Modified Files

### `src/app.html`
**Feature:** App title rebrand.

| What changed | Why |
|---|---|
| Line 118: `<title>Open WebUI</title>` → `<title>O&M Agent</title>` | Browser tab title for the client deployment. |

---

### `.env.example`
**Feature:** Invertix backend URL variable.

| What changed | Why |
|---|---|
| Added `VITE_INVERTIX_BACKEND=''` (after `OPENAI_API_BASE_URL`) | The feedback endpoint (`/v1/feedback`) lives on the FastAPI backend, not OpenWebUI. This env var points to the correct per-company Railway backend so thumbs up/down signals are routed to the right Langfuse project. Set to e.g. `https://backend-company-1-production.up.railway.app`. |

---

### `src/lib/constants.ts`
**Feature:** App name rebrand + dev URL fix.

| What changed | Why |
|---|---|
| Line 4: `APP_NAME = 'Open WebUI'` → `'O&M Agent'` | Shown in the UI header and notifications. |
| Lines 6-7: `WEBUI_HOSTNAME` and `WEBUI_BASE_URL` simplified to empty strings | In dev mode the upstream code constructs `http://localhost:8080` which conflicts with Vite's proxy. Setting both to `''` lets all API calls go through Vite's proxy (see `vite.config.ts`). |

---

### `vite.config.ts`
**Feature:** Dev-mode proxy to FastAPI backend.

| What changed | Why |
|---|---|
| Added `server.proxy` block (lines 7-12) proxying `/api`, `/ws`, `/oauth` to `http://localhost:3000` | In development (`npm run dev`) the FastAPI backend runs in Docker on port 3000. Without the proxy, browser API calls go to `localhost:5173` and 404. This makes `npm run dev` work end-to-end without changing any URL config. |

---

### `src/routes/+layout.svelte`
**Feature:** Notification text rebrand.

| What changed | Why |
|---|---|
| Lines 509, 641, 749: `'Open WebUI'` → `'O&M Agent'` in `new Notification(...)` calls | Browser push notification title matches the app name. Three locations: message done, chat update, general notification. |

---

### `src/lib/components/chat/Chat.svelte`
**Feature:** Invertix option picker + run_id / backend_url tracking per message.

| What changed | Why |
|---|---|
| Import `InvertixQuickDetails` (line ~117) | Mounts the option picker above the input. |
| Import `EmojiRatingPopup` + `{ emojiPopup }` store (near imports) | Renders emoji popup at root level. |
| `let pendingAskGroups` state variable | Holds grouped options from the stream until user picks or dismisses. |
| `submitPrompt` clears `pendingAskGroups` (first line of function) | Options are only relevant for the current turn. |
| `invertix:ask_options` handler in the SSE event listener: sets `pendingAskGroups = data.groups` | Populates the picker when the filter emits the event. |
| `invertix:run_meta` handler: `localStorage.setItem('inv_rid_' + message.id, data.run_id)` and `localStorage.setItem('inv_backend_' + message.id, data.backend_url)` | Persists run_id and the correct per-company backend URL per message so the feedback call goes to the right Railway service even after a process restart wipes the in-process cache. |
| `<InvertixQuickDetails>` rendered above `<MessageInput>` in the template | Conditionally shown when `pendingAskGroups.length > 0`. |
| `<EmojiRatingPopup>` rendered as sibling AFTER the root `</div>` (before `<style>`) | Must be outside all layout elements to avoid `position: fixed` being trapped by transform/opacity stacking contexts on message bubble animations. |

---

### `src/lib/components/chat/MessageInput.svelte`
**Feature:** Wire `onInjectText` to the `InputMenu`.

| What changed | Why |
|---|---|
| Added `onInjectText` prop passthrough to `<InputMenu>`: `onInjectText={(text) => { prompt = (prompt ? prompt + '\n' : '') + text; }}` | Lets the "Attach Artifact" flow in InputMenu prepend artifact references to the user's message. |

---

### `src/lib/components/chat/MessageInput/InputMenu.svelte`
**Feature:** "Attach Artifacts" tab in the `+` More menu.

| What changed | Why |
|---|---|
| Import `{ artifacts }` from `'$lib/stores/artifacts'` | Reads the artifact list. |
| Added `export let onInjectText: Function = () => {}` prop | Callback so the artifact picker can inject text into the chat input. |
| Helper functions `extractDocId`, `artifactDate`, `handleAttachArtifact` | `extractDocId` pulls `doc_XXXX` from the download URL; `handleAttachArtifact` formats the text injected into the prompt as `[Attached: name — document_id: xxx]` which the backend filter parses to resolve the artifact. |
| "Attach Artifacts" button added after "Reference Chats" in the main menu list (with badge showing count) | Entry point to the artifact picker tab. |
| `{:else if tab === 'artifacts'}` panel in the tab body | Lists all artifacts with type icons (image=`#73B2F2`, PDF=`#003877`, Excel=`#65B5E2`). Clicking inserts the reference into the prompt. |

---

### `src/lib/components/chat/Messages/ResponseMessage.svelte`
**Feature:** Download button, Langfuse feedback signals, emoji rating popup, removed unused controls.

#### Download button
| What changed | Why |
|---|---|
| `_downloadables` reactive state + `$:` block that regex-scans `message.content` for `[Download name](url)` and `![](url)` patterns | Agent embeds download links in the markdown stream; we surface them as a single download button instead of raw links. |
| `downloadFile(url, name)` helper | Fetches as blob then triggers `<a download>` so cross-origin URLs actually download instead of opening in a new tab. Falls back to anchor click if CORS blocks the fetch. |
| Download button in the action bar (replaces "Read Aloud" button) | Shown only when `downloadables.length > 0`. Downloads all artifacts in one click. |

#### Feedback signals to Langfuse
| What changed | Why |
|---|---|
| `sendFeedback(signal, value, comment?)` function | POSTs to `${VITE_INVERTIX_BACKEND}/v1/feedback` (or per-message `inv_backend_<msgId>` from localStorage). Reads `inv_rid_<msgId>` to get the run_id. Silent (fire-and-forget). |
| `sendFeedback('copy_to_clipboard', 1)` in `copyToClipboard` | Tracks when users copy agent output. |
| `sendFeedback('user_feedback', rating)` in `feedbackHandler` (rating === 1 or -1) | Core thumbs up/down signal to Langfuse. Also triggers emoji popup via `emojiPopup.open(...)`. |
| `sendFeedback('regenerate', 1)` in all three regenerate click handlers | Tracks regeneration requests. |
| Thumbs up/down now open `EmojiRatingPopup` via `emojiPopup.open(...)` instead of OpenWebUI's built-in rate comment | Provides richer 4-level rating; avoids OpenWebUI's rating dialog which duplicates feedback. |
| `showRateComment = true` commented out | Disables OpenWebUI's built-in rating text box; Langfuse signals replace it. |

#### Removed upstream controls
| What changed | Why |
|---|---|
| "Edit" button removed from action bar | Not needed in agent UI; users can't edit agent responses. |
| "Read Aloud" (TTS) button removed | Replaced by Download button. |
| "Continue Response" button removed | Agent runs are atomic; continuation doesn't apply. |

---

### `src/lib/components/chat/Messages/Markdown/MarkdownInlineTokens.svelte`
**Feature:** Constrain inline image size.

| What changed | Why |
|---|---|
| Line 99: `<Image src=... />` → `<Image src=... className="block max-w-[480px] w-full" />` | Agent chart images were rendering at full viewport width. Constrained to 480px max. |

---

### `src/lib/components/common/ImagePreview.svelte`
**Feature:** Simplified image preview modal with download.

| What changed | Why |
|---|---|
| Removed `PanzoomContainer` import and usage | Panzoom caused scroll-locking issues inside the chat layout. |
| Modal background changed to `bg-black/20` (semi-transparent) | Full black background obscured context; lighter overlay feels less jarring. |
| Click-outside-to-close added: `on:click` on the backdrop div | Standard modal UX. |
| `downloadImage()` async function added | Downloads the previewed chart; handles base64 data URLs, fetch-as-blob, and CORS fallback. |
| Download button added to the modal controls | One-click save from preview. |
| Preview constrained to `max-width: 65vw; max-height: 65vh` | Prevents oversized charts from filling the screen. |
| Removed `console.log('Escape')` debug line | Cleanup. |

---

### `src/lib/components/layout/Sidebar.svelte`
**Feature:** Client logo in sidebar header + Artifacts panel.

#### Logo
| What changed | Why |
|---|---|
| `items-center` added to sidebar header div class | Logo was vertically misaligned with the nav icons. |
| Logo `<a>` class changed from `flex items-center rounded-xl size-8.5 h-full justify-center ...` to `flex items-center px-2 py-1 hover:opacity-80 ...` | Simplified click target for the logo. |
| `<img src="/static/favicon.png" class="sidebar-new-chat-icon size-6 rounded-full">` replaced with `<img src="/enerparc-full-logo.png" class="h-[26px] w-auto object-contain" alt="Enerparc">` | Replaces OpenWebUI favicon with the client's full logo. Swap `enerparc-full-logo.png` for the target client's logo file. |
| Removed `<a href="/">` app name text link next to the logo | Name is now embedded in the logo image. |

#### Artifacts panel
| What changed | Why |
|---|---|
| Import `ArtifactsPanel` and `{ artifacts }` store | Mounts the artifacts list in the sidebar. |
| `let showArtifacts = false` state | Controls open/closed state of the Artifacts folder. |
| `<Folder id="sidebar-artifacts" ...>` block added at bottom of sidebar nav (after the last existing Folder) | Shows all generated artifacts (charts/PDFs/Excel) from the current session. Each item has a Download and Delete button. Empty state shows a placeholder message. |

---

### `src/lib/components/chat/Placeholder.svelte` / `ChatPlaceholder.svelte`
**Feature:** Replaced generic suggestions with Enerparc-specific prompt starters.

| What changed | Why |
|---|---|
| Suggestion cards updated to solar O&M domain prompts | Generic OpenWebUI suggestions ("Write a creative story", etc.) replaced with relevant prompts like "Show me last month's PR curve" or "Generate an O&M report for Plant X". |

---

### `src/lib/components/chat/Suggestions.svelte`
**Feature:** Domain-specific quick-start suggestions.

| What changed | Why |
|---|---|
| Suggestion list replaced with Enerparc / O&M Agent relevant prompts | Same reason as Placeholder — contextual suggestions reduce onboarding friction. |

---

### Other minor changes (model selector, user message, channel components)
| File | Change | Why |
|---|---|---|
| `src/lib/components/chat/ModelSelector/Selector.svelte` | Hides or simplifies model picker | Only one model available (`O&M Agent`); full selector is noise. |
| `src/lib/components/chat/Messages/UserMessage.svelte` | Minor styling tweak | Alignment consistency with agent message bubbles. |
| `src/lib/components/channel/MessageInput.svelte` | Same `onInjectText` wire-up as chat `MessageInput` | Channels share the same input component. |
| `src/lib/components/channel/Messages/Message.svelte` | Minor | Mirrors ResponseMessage changes for channel context. |
| `src/lib/components/chat/ContentRenderer/FloatingButtons.svelte` | Minor | Floating toolbar adjustments. |
| `src/lib/components/chat/Messages/ResponseMessage/RegenerateMenu.svelte` | `sendFeedback('regenerate', 1)` added | Same regenerate tracking as the main ResponseMessage regenerate handler. |

---

## Environment Variables Required

Copy these into your `.env` before running:

```env
VITE_INVERTIX_BACKEND=https://<your-backend>.up.railway.app
```

All other env vars follow the standard OpenWebUI `.env.example`.

---

## Filter (OpenWebUI Admin → Functions)

The stream filter is not part of the SvelteKit source — it lives in the OpenWebUI database and must be pasted manually:

1. OpenWebUI Admin → Functions → New Function
2. Paste the contents of `../backend/openwebui/invertix_filter.py` (relative to this repo root)
3. Save

The filter:
- Strips `<!--ASK:...-->` tags and emits `invertix:ask_options` → drives the option picker
- Strips `<!--INVERTIX-DOC:...-->` tags and emits `invertix:doc_ready` → drives doc cards
- Strips `<!--INVERTIX-STEP:...-->` and emits `invertix:step` → drives step timeline
- Parses `<!--INVERTIX-META:run_id=...,backend_url=...-->` and emits `invertix:run_meta` → enables per-message feedback routing to the correct per-company backend

This filter must be re-pasted any time `backend/openwebui/invertix_filter.py` is updated.
