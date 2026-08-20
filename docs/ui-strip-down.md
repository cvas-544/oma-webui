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

### 1. Sidebar
**File:** `src/lib/components/layout/Sidebar.svelte` — **RED** (FORK-GUIDE § 2)

| Element | How to identify in code | Strip / Keep | Reason |
|---|---|---|---|
| Workspace section | `pinnedItems` includes `'workspace'`; rendered via `case 'workspace':` block and the pinned menu loop | **Strip** | Prompts / Tools / Functions / Models / Knowledge — all advanced; not needed in v1 |
| Notes | `case 'notes':` block; `pinnedNotes`, `PinnedNoteList` | **Strip** | Not part of O&M workflow |
| Channels | `showChannels`, `getChannels` import, channel list render block | **Strip** | No channels in OMA v1 |
| Calendar | `case 'calendar':` block; `CalendarIcon` import | **Strip** | Not part of O&M workflow |
| Automations | `case 'automations':` block | **Strip** | Developer feature — not for O&M users |
| Playground | `case 'playground':` block | **Strip** | Developer feature — not for O&M users |
| Folders | `Folders` component import; `showFolders`, `showCreateFolderModal` state; folder drag-and-drop handlers | **Strip** | Chat organisation unnecessary for v1; adds confusion |
| Shared Folders | `SharedFolderItem` import; `sharedFolders` state; `getSharedFolders` call | **Strip** | Not needed in v1 |
| Pinned Models list | `PinnedModelList` import; `showPinnedModels` state | **Strip** | Users don't choose models |
| Archived chats link | Rendered via `$user?.permissions` check — already gated; confirm hidden | **Confirm** | Verify the permission gate already hides it for `user` role |
| Temporary chat toggle | `temporaryChatEnabled` store; toggle button near new-chat area | **Strip** | Confusing for non-technical users |

**Risk:** Sidebar.svelte is RED — any change here must be re-applied carefully on upstream upgrades. Keep each strip as a minimal `{#if}` wrap around the render block, not a logic removal.

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
