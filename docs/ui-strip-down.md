# OMA WebUI — UI Strip-Down Audit

**Applies to:** OMA v0.11.0 (OpenWebUI fork)  
**Read alongside:** `FORK-GUIDE.md` — file classification (Green/Yellow/Red) and comment conventions apply here too  
**Purpose:** Audit of all OpenWebUI UI surfaces that should be hidden or disabled for O&M users in v1. Admin users retain full access.

---

## Guiding Principle

> An O&M expert opening this tool for the first time should see only what they need: a chat interface, their history, and our custom outputs (steps card, doc card, charts). Everything else is noise.

**Standard hide pattern** — wrap the element:
```svelte
{#if $user?.role !== 'user'}
  <!-- element -->
{/if}
```

**Standard disable comment** (when commenting out rather than wrapping):
```svelte
<!-- OMA: disabled — <reason> -->
```

Both conventions follow `FORK-GUIDE.md` § Don'ts ("Comment them out with a `// OMA: disabled —` note").

---

## How to Apply (Implementation Workflow)

1. Pick one surface at a time (one file per PR)
2. Wrap or comment the element — **do not delete**
3. Test as a regular user (`vasuch544@gmail.com` / `admin@123` — switch role to `user` in admin panel)
4. Test as admin to confirm full UI still visible
5. Update `Changes.md` with the surface + what was wrapped
6. Commit on `v0.11.0` branch

---

## Surface-by-Surface Audit

---

### 3. Home Page (Chat Input + Suggestions)
**Files:**
- `src/lib/components/chat/MessageInput.svelte` — **RED**
- `src/lib/components/chat/MessageInput/InputMenu.svelte` — **RED**
- Component containing Suggested prompts (likely `src/routes/(app)/+page.svelte` or `src/lib/components/chat/Suggestions.svelte`)

**Screenshot:** `screenshots/annotated-03-home.png`
**Confirmed by:** Vasu — 2026-08-20

| Element | How to identify in code | Decision | Reason |
|---|---|---|---|
| ✦ Integrations icon (sparkle, left of input) | Button in input toolbar; `InputMenu` trigger with sparkle/plus-sparkle icon | **STRIP ✓** | No integrations in O&M v1 workflow |
| Model selector (dropdown + chevron, right of input) | `<ModelSelector>` or inline model name button; `showModelSelector` prop | **MAKE STATIC ✓** | O&M users don't choose models — show name only, no dropdown |
| Mic / Dictate button | Mic icon button; `VoiceRecording` or `startRecording` handler | **STRIP ✓** | Dictate = future feature |
| Voice/waveform button | Waveform icon button right of mic; voice mode handler | **REPLACE → Send ✓** | Replace with Send icon (use OMA/OpenWebUI send icon); dictate+voice come later |
| Suggested section (label + 3 generic prompts) | `{#each suggestions as suggestion}` or `<Suggestions>` component | **STRIP ✓** | Generic prompts irrelevant to O&M; replace with O&M-specific suggestions UI |

**New O&M Suggestions UI** (replaces Suggested section):
- Design TBD — will use O&M-relevant quick-start prompts (e.g., "Show me yesterday's generation report", "Summarise alarms for Plant X")
- New component: `src/lib/components/chat/OmaSuggestions.svelte`
- i18n wrapped; German primary

**Strip strategy:** applies to **all users** (no role gate). Original code kept in `{#if false}` blocks or HTML comments — uncomment to re-enable for staging/production.

**How implemented:**
- Integrations menu + divider: `{#if false}` block in `MessageInput.svelte`
- Dictate button: `{#if false}` block in `MessageInput.svelte`
- Voice mode: `{#if false && ...}` → always falls through to Send button
- Model selector: replaced with static `<span>` text; original `<ModelSelector />` in HTML comment
- Suggestions: `<OmaSuggestions>` mounted unconditionally; original `<Suggestions>` in HTML comment
- Send button: color changed from `bg-black` → `bg-[#003877]` (Enerparc blue)

**Input field layout & sizing (implemented):**
- Layout: `+` button and Send button are `absolute` inside `#message-input-container` (`relative`); text area uses `pl-10 pr-12` to leave room for both
- `+` wrapper: `absolute left-2 top-1/2 -translate-y-1/2 z-10` — perfectly centered regardless of box height
- Send wrapper: `absolute top-1/2 -translate-y-1/2 right-2` — same centering
- Height ~30% taller: `#chat-input-container` uses `pt-4 pb-3` (was `pt-2 pb-0.5`); `text-base` explicit
- `+` button: `size-10` (40 px), icon `size-6`; was `size-[1.875rem]`/`size-5`
- Send button: `p-[7px]`, icon `size-6`; was `p-[5px]`/`size-5`
- `InputMenu.svelte` tooltip placement changed to `"top"` to avoid inline text rendering bug

**Risk:** RED files — wrap/comment only, no logic deletes.

---

### 1. Sidebar
**File:** `src/lib/components/layout/Sidebar.svelte` — **RED** (FORK-GUIDE § 2)
**Screenshot:** `screenshots/annotated-01-sidebar.png`
**Confirmed by:** Vasu — 2026-08-20

| Element | How to identify in code | Decision | Reason |
|---|---|---|---|
| Notes | `case 'notes':` block; `pinnedNotes`, `PinnedNoteList` | **STRIP ✓** | Not part of O&M workflow |
| Workspace section | `pinnedItems` includes `'workspace'`; rendered via `case 'workspace':` block and the pinned menu loop | **STRIP ✓** | Prompts / Tools / Functions / Models / Knowledge — admin only |
| Folders | `Folders` component import; `showFolders`, `showCreateFolderModal` state; folder drag-and-drop handlers | **STRIP ✓** | Unnecessary for v1; adds confusion |
| Channels | `showChannels`, `getChannels` import, channel list render block | **STRIP** | No channels in OMA v1 |
| Calendar | `case 'calendar':` block; `CalendarIcon` import | **STRIP** | Not part of O&M workflow |
| Automations | `case 'automations':` block | **STRIP** | Developer feature — not for O&M users |
| Playground | `case 'playground':` block | **STRIP** | Developer feature — not for O&M users |
| Shared Folders | `SharedFolderItem` import; `sharedFolders` state; `getSharedFolders` call | **STRIP** | Not needed in v1 |
| Pinned Models list | `PinnedModelList` import; `showPinnedModels` state | **STRIP** | Users don't choose models |
| Temporary chat toggle | `temporaryChatEnabled` store; toggle button near new-chat area | **STRIP** | Confusing for non-technical users |
| Archived chats link | Rendered via `$user?.permissions` check — already gated; confirm hidden | **CONFIRM** | Verify the permission gate already hides it for `user` role |
| Enerparc logo | `<img src="/enerparc-logo.png">` at top of sidebar | **KEEP** | Brand identity |
| New Chat button | Near top of sidebar | **KEEP** | Core action |
| Search | Sidebar nav item | **KEEP** | Core action |
| Artifacts section | Custom OMA store — `artifacts.ts` | **KEEP** | Core OMA feature |
| Chats + history list | Session list render block | **KEEP** | Core feature |

**How to implement:**
```svelte
{#if $user?.role !== 'user'}
  <!-- wrap each STRIP block individually -->
{/if}
```
Wrap each block separately — do not delete. One `{#if}` per element so upstream diffs stay clean.

**Risk:** RED file — re-apply wraps carefully on upstream upgrades.

---

### 2. Search Modal
**Files:** `src/lib/components/layout/SearchModal.svelte` — **YELLOW** · `src/lib/components/layout/Sidebar/SearchInput.svelte` — **RED**
**Screenshot:** `screenshots/annotated-02-search.png`
**Confirmed by:** Vasu — 2026-08-20
**Status:** IMPLEMENTED ✓ (build clean, tested)

| Element | How to identify in code | Decision | Reason |
|---|---|---|---|
| Actions section ("Start a new conversation", "Create a new note") | `{#each actions as action}` block + `actions[]` array | **STRIP ✓** | Not part of O&M workflow — users don't start meta-actions from search |
| `folder:` filter prefix | `options[]` in `SearchInput.svelte`; `initItems` folder branch | **STRIP ✓** | Folders stripped from sidebar — filter is meaningless |
| `pinned:` filter prefix | `options[]` + `initItems` pinned branch | **STRIP ✓** | Pinning not an O&M workflow |
| `shared:` filter prefix | `options[]` + `initItems` shared branch | **STRIP ✓** | No sharing in v1 |
| `archived:` filter prefix | `options[]` + `initItems` archived branch | **STRIP ✓** | Not exposed to users |
| `tag:` filter prefix | `options[]` entry; `initItems` tag branch; reads `$tags` store | **KEEP ✓** | Tag search still useful for power users |
| Search input | `<SearchInput bind:value={query}>` | **KEEP** | Core |
| Chat results list | `{#each chatList as chat}` block | **KEEP** | Core |
| Right preview panel (chat) | `<Messages>` component in right column | **KEEP** | Core |
| Filter tabs (Chats / Images / Files) | NEW — `activeTab` state + tab bar | **ADDED ✓** | Replaces Actions; lets users filter by content type |
| Artifact results list | NEW — `filteredArtifacts` from `$artifacts` store | **ADDED ✓** | Images and Files from S3-backed artifact store |
| Artifact detail panel | NEW — right panel when `activeTab !== 'chats'` | **ADDED ✓** | Name, type badge, date, Download button; image thumbnail |

**i18n:** All new strings wrapped with `$i18n.t()`. `"Select a file to preview"` added to `de-DE` (`"Datei zur Vorschau auswählen"`) and `en-US` locale files.

---

### 2. Navbar
**File:** `src/lib/components/chat/Navbar.svelte` — **YELLOW** (FORK-GUIDE § 2)

| Element | How to identify in code | Strip / Keep | Reason |
|---|---|---|---|
| Model selector | `<ModelSelector>` inside `{#if showModelSelector}` block | **Strip** | OMA runs one model — users should not pick or even see model names |
| Share chat button / modal | `<ShareChatModal>` mount + trigger button using `shareEnabled` prop | **Strip** | No sharing workflow in v1 |

**How:** Pass `showModelSelector={false}` from the parent that mounts `<Navbar>`, or wrap the `ModelSelector` block with a role check inside the component.  
**Risk:** Low — YELLOW file, shallow change.

---

### 3. Chat Input
**File:** `src/lib/components/chat/MessageInput.svelte` — **RED**  
**File:** `src/lib/components/chat/MessageInput/InputMenu.svelte` — **RED**

| Element | How to identify in code | Strip / Keep | Reason |
|---|---|---|---|
| Web search toggle | `showWebSearchButton` reactive var; `onWebSearchToggle` prop; rendered as a button near the input toolbar | **Strip** | O&M data lives in the agent's DB — web search is irrelevant and confusing |
| Tools selector | `showToolsButton` reactive var (true when `$tools.length > 0`); tools panel toggle button | **Strip** | Tool selection is an admin/developer concern |
| Image generation | `showImageGenerationButton` reactive var; gated by `$config.features.enable_image_generation` | **Strip** | Not part of O&M workflow |
| Voice / audio recording | `VoiceRecording` component import; `recording` state; mic button in input toolbar | **Strip** | Not needed in v1 |
| Screen capture | Screen share / capture handler block inside `MessageInput` | **Strip** | Not part of O&M workflow |
| File upload | `uploadFile` import; file input; `onUpload` prop | **Keep** | Users may need to attach plant data exports or images |

**Risk:** RED files — these are the highest-churn upstream files. Prefer wrapping via the `showXxx` reactive vars (e.g. force `showWebSearchButton = false` at the top of the `<script>` block) rather than removing render blocks, so the upstream logic is untouched.

---

### 4. Message Actions (per-message toolbar)
**File:** `src/lib/components/chat/Messages/ResponseMessage.svelte` — **RED**

| Element | How to identify in code | Strip / Keep | Reason |
|---|---|---|---|
| TTS / speak button | Rendered inside `{#if !readOnly && ($user?.role === 'admin' \|\| ($user?.permissions?.chat?.tts ?? true))}` | **Strip** | Already partially gated — set `tts` permission to `false` for users via admin panel (no code change needed) |
| Share message button | Block using `shareEnabled` prop or a share icon button in the action row | **Strip** | No sharing workflow in v1 |
| Edit message | Gated by `{#if $user?.role === 'user' ? ($user?.permissions?.chat?.edit ?? true) : true}` | **Strip** | Editing agent messages confuses the conversation history; disable via admin panel permission |
| Copy to clipboard | Copy button in action row | **Keep** | Useful and expected |
| Regenerate | Gated by `$user?.permissions?.chat?.regenerate_response`; our emoji popup triggers alongside | **Keep** | Useful when agent gives a wrong answer |
| Our emoji rating popup | `emojiPopup.open(...)` wired to thumbs-up/down | **Keep** | Core feedback mechanism |
| Our doc download card | `InvertixDocCard` rendered below message | **Keep** | Core OMA feature |

**Risk:** RED file. TTS and Edit can be disabled via the admin panel permissions UI without touching code — do that first before any code change.

---

### 5. Controls Panel (right side)
**File:** `src/lib/components/chat/Chat.svelte` — **RED**  
**Store:** `showControls` in `$lib/stores`

| Element | Strip / Keep | Reason |
|---|---|---|
| Entire controls panel (system prompt, advanced params, temperature, top-p, etc.) | **Strip** | Advanced LLM parameters — meaningless and dangerous for O&M users to touch |
| Toggle button that opens the panel | **Strip** | Remove the trigger so users can't open it |

**How:** Override `showControls` to always `false` for `user` role. Wrap the controls toggle button with `{#if $user?.role !== 'user'}`.  
**Risk:** RED file — minimal change (one `{#if}` on the toggle button).

---

### 6. Routes — Restrict for Users

These are full pages that O&M users should never reach. OpenWebUI's own permission system partially gates some of these, but the links still appear in the sidebar. Strip the sidebar links (covered in § 1) and add a redirect guard in each route's `+page.svelte` or `+layout.svelte`.

| Route | File | Strip / Keep | Reason |
|---|---|---|---|
| `/workspace` (and all sub-routes) | `src/routes/(app)/workspace/` | **Strip** | Prompts, Tools, Functions, Models, Knowledge — developer/admin only |
| `/workspace/models` | sub-route | **Strip** | — |
| `/workspace/knowledge` | sub-route | **Strip** | — |
| `/workspace/prompts` | sub-route | **Strip** | — |
| `/workspace/tools` | sub-route | **Strip** | — |
| `/workspace/functions` | sub-route | **Strip** | — |
| `/workspace/skills` | sub-route | **Strip** | — |
| `/playground` | `src/routes/(app)/playground/` | **Strip** | Developer sandbox |
| `/channels` | `src/routes/(app)/channels/` | **Strip** | Not used in OMA v1 |
| `/notes` | `src/routes/(app)/notes/` | **Strip** | Not part of O&M workflow |
| `/calendar` | `src/routes/(app)/calendar/` | **Strip** | Not part of O&M workflow |
| `/automations` | `src/routes/(app)/automations/` | **Strip** | Developer/admin feature |
| `/admin` | `src/routes/(app)/admin/` | **Keep (admin only)** | Already gated by OpenWebUI — confirm it stays that way |

**How to guard:** Add to each route's `+page.svelte` or parent `+layout.svelte`:
```svelte
<script>
  import { user } from '$lib/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  onMount(() => {
    if ($user?.role === 'user') goto('/');
  });
</script>
```

**Risk:** GREEN files for new guards added; touching existing `+layout.svelte` files is YELLOW.

---

### 7. Settings Page
**File:** `src/routes/(app)/admin/settings/` and user-facing settings modal

| Section | Strip / Keep | Reason |
|---|---|---|
| Account (name, password) | **Keep** | Users need this |
| Interface (language, theme) | **Keep** | Useful — our theme is here too |
| Connections | **Strip** | Admin only — users should never see backend URL config |
| Models | **Strip** | Users don't manage models |
| Audio / TTS | **Strip** | Disabled feature; no need to expose |
| About | **Keep** | Harmless, shows version info |

---

## What to Leave Alone (Do Not Strip)

| Feature | Why |
|---|---|
| Chat history (sidebar) | Core — users need their conversation history |
| New chat button | Core |
| Our `InvertixStepsCard` | Core OMA feature |
| Our `InvertixDocCard` + download | Core OMA feature |
| Our `InvertixChartCard` | Core OMA feature |
| Our `EmojiRatingPopup` + feedback pills | Core feedback mechanism |
| Our `QuickSettingsMenu` | Replaces all the settings noise with one simple menu |
| Our `WeeklySurvey` | Core feedback mechanism |
| File upload in chat | Users may need to paste plant exports |
| Copy to clipboard | Expected basic action |
| Regenerate | Useful when agent answers incorrectly |

---

## Suggested Implementation Order

Do one surface per PR. Low-risk first:

1. **Admin panel only** (no code) — disable TTS permission + edit permission for user role in OpenWebUI Admin → Users → Permissions
2. **Routes** — add `onMount` redirect guards to workspace, playground, channels, notes, calendar, automations
3. **Navbar** — hide model selector + share button (YELLOW — low risk)
4. **Sidebar** — strip workspace, notes, channels, calendar, automations, playground, folders, pinned models, temporary chat (RED — do carefully, one block at a time)
5. **Controls panel** — wrap toggle button with role check (RED — minimal)
6. **Chat input** — force `showWebSearchButton`, `showToolsButton`, `showImageGenerationButton`, `recording` to false for user role (RED — touch only reactive vars, not render blocks)
7. **Settings page** — hide Connections + Models + Audio sections

---

## Files Touched Summary (FORK-GUIDE Classification)

| File | Classification | Change type |
|---|---|---|
| `src/lib/components/layout/Sidebar.svelte` | RED | Wrap 8–9 blocks with `{#if $user?.role !== 'user'}` |
| `src/lib/components/chat/Navbar.svelte` | YELLOW | Wrap model selector + share modal |
| `src/lib/components/chat/MessageInput.svelte` | RED | Override 4 `showXxx` vars to false for user role |
| `src/lib/components/chat/Messages/ResponseMessage.svelte` | RED | Wrap share button; TTS + edit via admin panel |
| `src/lib/components/chat/Chat.svelte` | RED | Wrap controls panel toggle |
| `src/routes/(app)/workspace/+layout.svelte` | YELLOW | Add role redirect guard |
| `src/routes/(app)/playground/+page.svelte` | YELLOW | Add role redirect guard |
| `src/routes/(app)/channels/+page.svelte` | YELLOW | Add role redirect guard |
| Other restricted route pages | YELLOW | Add role redirect guard |
