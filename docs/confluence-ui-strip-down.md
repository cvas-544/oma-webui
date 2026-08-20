# OMA WebUI v0.11.0 — UI Strip-Down (Confluence)

Copy each surface table directly into Confluence. Use **Insert > Table** or paste in the wiki editor.

Legend: 🔴 Strip &nbsp;|&nbsp; 🟡 Change &nbsp;|&nbsp; 🟢 Keep

---

## Surface 1 — Sidebar

**File:** `src/lib/components/layout/Sidebar.svelte` (RED — high churn risk)
**Screenshot:** `annotated-01-sidebar.png`
**Reviewed:** 2026-08-20

| Element | Decision | File | Code pointer | Notes |
|---|---|---|---|---|
| Notes | 🔴 Strip | `Sidebar.svelte` | `case 'notes':` block; `pinnedNotes`, `PinnedNoteList` | Wrap with `{#if $user?.role !== 'user'}` |
| Workspace | 🔴 Strip | `Sidebar.svelte` | `case 'workspace':` block; `pinnedItems` workspace entry | Wrap with `{#if $user?.role !== 'user'}` |
| Folders | 🔴 Strip | `Sidebar.svelte` | `Folders` component; `showFolders`, `showCreateFolderModal`; drag handlers | Wrap with `{#if $user?.role !== 'user'}` |
| Channels | 🔴 Strip | `Sidebar.svelte` | `showChannels`, `getChannels` import, channel list block | Wrap with `{#if $user?.role !== 'user'}` |
| Calendar | 🔴 Strip | `Sidebar.svelte` | `case 'calendar':` block; `CalendarIcon` import | Wrap with `{#if $user?.role !== 'user'}` |
| Automations | 🔴 Strip | `Sidebar.svelte` | `case 'automations':` block | Wrap with `{#if $user?.role !== 'user'}` |
| Playground | 🔴 Strip | `Sidebar.svelte` | `case 'playground':` block | Wrap with `{#if $user?.role !== 'user'}` |
| Shared Folders | 🔴 Strip | `Sidebar.svelte` | `SharedFolderItem`; `sharedFolders`; `getSharedFolders` | Wrap with `{#if $user?.role !== 'user'}` |
| Pinned Models | 🔴 Strip | `Sidebar.svelte` | `PinnedModelList`; `showPinnedModels` | Wrap with `{#if $user?.role !== 'user'}` |
| Temporary chat toggle | 🔴 Strip | `Sidebar.svelte` | `temporaryChatEnabled` store + toggle button | Wrap with `{#if $user?.role !== 'user'}` |
| Archived chats link | ⚠️ Confirm | `Sidebar.svelte` | `$user?.permissions` gate — verify it already hides for `user` role | Check in admin panel before touching code |
| Enerparc logo | 🟢 Keep | — | `<img src="/enerparc-logo.png">` | Brand identity |
| New Chat | 🟢 Keep | — | — | Core action |
| Search | 🟢 Keep | — | — | Core action |
| Artifacts section | 🟢 Keep | — | Custom OMA — `artifacts.ts` | Core OMA feature |
| Chats + history | 🟢 Keep | — | Session list render block | Core feature |

---

---

## Surface 2 — Search Modal

**Files:** `SearchModal.svelte` (YELLOW) · `Sidebar/SearchInput.svelte` (RED)
**Screenshot:** `annotated-02-search.png`
**Reviewed:** 2026-08-20
**Status:** ✅ Implemented + tested

| Element | Decision | File | Code pointer | Notes |
|---|---|---|---|---|
| Actions section ("Start a new conversation", "Create a new note") | 🔴 Strip | `SearchModal.svelte` | `{#each actions as action}` block + `actions[]` array | Commented out with OMA note |
| `folder:` filter prefix | 🔴 Strip | `SearchInput.svelte` | `options[]` array entry; `initItems` folder branch | Removed — folders stripped from sidebar |
| `pinned:` filter prefix | 🔴 Strip | `SearchInput.svelte` | `options[]` + `initItems` pinned branch | Removed |
| `shared:` filter prefix | 🔴 Strip | `SearchInput.svelte` | `options[]` + `initItems` shared branch | Removed — no sharing in v1 |
| `archived:` filter prefix | 🔴 Strip | `SearchInput.svelte` | `options[]` + `initItems` archived branch | Removed |
| `tag:` filter prefix | 🟢 Keep | `SearchInput.svelte` | `options[]` entry; `initItems` tag branch | Useful for chat tagging |
| Search input | 🟢 Keep | `SearchModal.svelte` | `<SearchInput bind:value={query}>` | Core |
| Chat results list | 🟢 Keep | `SearchModal.svelte` | `{#each chatList as chat}` block | Core |
| Right preview panel | 🟢 Keep | `SearchModal.svelte` | `<Messages>` in right column | Core |
| Filter tabs (Chats / Images / Files) | 🟡 Added | `SearchModal.svelte` | `activeTab` state + tab bar above results | Replaces Actions section |
| Artifact results list | 🟡 Added | `SearchModal.svelte` | `filteredArtifacts` from `$artifacts` store | Images + Files from S3 artifact store |
| Artifact detail panel | 🟡 Added | `SearchModal.svelte` | Right panel when `activeTab !== 'chats'` | Name, type badge, date, Download button; image thumbnail |

**i18n:** All new strings use `$i18n.t()`. New key `"Select a file to preview"` → `"Datei zur Vorschau auswählen"` added to `de-DE` and `en-US`.

---

---

## Surface 3 — Home Page (Chat Input + Suggestions)

**Files:** `MessageInput.svelte` (RED) · `InputMenu.svelte` (RED) · Suggestions component (TBD)
**Screenshot:** `annotated-03-home.png`
**Reviewed:** 2026-08-20

| Element | Decision | File | Code pointer | Notes |
|---|---|---|---|---|
| ✦ Integrations icon (sparkle, left of input) | 🔴 Strip | `MessageInput.svelte` / `InputMenu.svelte` | `InputMenu` trigger button with sparkle icon | Comment out with OMA note — no integrations in v1 |
| Model selector (dropdown + chevron) | 🟡 Change → static | `MessageInput.svelte` | `<ModelSelector>` or `showModelSelector` prop | Show model name as plain text for `user` role; no dropdown, no chevron |
| Mic / Dictate button | 🔴 Strip | `MessageInput.svelte` | Mic icon button; `startRecording` / `VoiceRecording` handler | Future feature — comment out |
| Voice / waveform button | 🟡 Change → Send | `MessageInput.svelte` | Waveform icon button right of mic; voice mode handler | Replace with Send icon (OpenWebUI send icon); wire to `submitPrompt` |
| Suggested section (label + 3 generic prompts) | 🔴 Strip | `+page.svelte` or `Suggestions.svelte` | `{#each suggestions}` block or `<Suggestions>` component | Replace with new `<OmaSuggestions>` component |
| O&M Suggestions (new) | 🟡 Add | `OmaSuggestions.svelte` (new) | New component | O&M-specific quick-start prompts; i18n; German primary |
| Input field height | 🟡 Change | `MessageInput.svelte` | `#chat-input-container` — `pt-4 pb-3 text-base` (was `pt-2 pb-0.5`) | ~30% taller; more breathing room |
| `+` button size | 🟡 Change | `MessageInput.svelte` | `size-10` icon `size-6` (was `size-[1.875rem]`/`size-5`) | Proportional to taller input |
| Send button size | 🟡 Change | `MessageInput.svelte` | `p-[7px]` icon `size-6` (was `p-[5px]`/`size-5`) | Proportional to taller input |
| `+` / Send vertical centering | 🟡 Change | `MessageInput.svelte` | Both use `top-1/2 -translate-y-1/2` (absolute) | Stays centered regardless of box height |

**Strip scope:** applies to all users (no role gate). Original code kept in `{#if false}` / HTML comments for easy re-enable.
**i18n:** All new strings in `OmaSuggestions.svelte` use `$i18n.t()`. O&M suggestion texts added to `de-DE` and `en-US` locale files.

---

<!-- Next surface tables will be added here as screenshots are reviewed -->
