# OpenWebUI Fork — Maintenance Guide

**Applies to:** Any deployment that forks OpenWebUI and customises it for a client (Invertix, office UI, etc.)
**Read alongside:** `CHANGES.md` (what we changed and why)

---

## 1. The Golden Rule

> **Add, never modify. Extend, never replace.**

Every file you modify in the upstream OpenWebUI source is a future merge conflict waiting to happen. New files you create (new components, new stores, new static assets) survive upstream upgrades with zero conflict. The fewer upstream files you touch, the cheaper every upgrade is.

---

## 2. File Classification

### Green — Safe to own (create new, modify freely)
These are files we introduced. They don't exist in upstream OpenWebUI so they will never conflict.

```
src/lib/components/chat/Invertix*.svelte       ← all new Invertix components
src/lib/components/chat/Messages/EmojiRatingPopup.svelte
src/lib/components/layout/Sidebar/ArtifactsPanel.svelte
src/lib/stores/artifacts.ts
src/lib/stores/emojiPopup.ts
static/enerparc-full-logo.png
static/enerparc-logo.png
CHANGES.md
FORK-GUIDE.md
```

### Yellow — Touched but shallow (review on every upstream upgrade)
We modified these files but only at the surface — a string replacement, a one-line addition, or a small block. Conflicts here are easy to resolve because the change is isolated.

```
src/app.html                        ← title only
src/lib/constants.ts                ← APP_NAME + 2 URL lines
vite.config.ts                      ← proxy block only
src/routes/+layout.svelte           ← 3 notification strings only
.env.example                        ← one new variable
```

### Red — Deep modifications (highest merge risk, review carefully)
We made substantial changes to these upstream files. Every upstream upgrade must be diffed carefully before accepting.

```
src/lib/components/chat/Chat.svelte
src/lib/components/chat/MessageInput.svelte
src/lib/components/chat/MessageInput/InputMenu.svelte
src/lib/components/chat/Messages/ResponseMessage.svelte
src/lib/components/chat/Messages/Markdown/MarkdownInlineTokens.svelte
src/lib/components/common/ImagePreview.svelte
src/lib/components/layout/Sidebar.svelte
src/lib/components/chat/Placeholder.svelte
src/lib/components/chat/Suggestions.svelte
```

---

## 3. Do's

**Do create new Svelte components** for every new UI feature. Name them with a client prefix (`Invertix`, `Enerparc`) so they're instantly recognisable as custom code and never confused with upstream files.

**Do use Svelte stores** to communicate between a custom component and an upstream component (e.g. `emojiPopup.ts` lets `ResponseMessage.svelte` open a popup that `Chat.svelte` renders at the root). This keeps the change in the upstream file to a single import + one event listener line.

**Do keep upstream file edits as small as possible.** One import line + one event handler line is ideal. The less you change, the less you maintain.

**Do document every change in `CHANGES.md`** immediately when you make it — file, line range, what and why. Future you will thank you at upgrade time.

**Do keep a clean git history in this repo.** One commit per feature makes it easy to cherry-pick your changes onto a new upstream base.

**Do test the full golden path** after every upstream merge:
- Login
- Send a message → agent responds and streams
- Option picker appears and works
- Thumbs up / down opens emoji popup, score posts to Langfuse
- Download button appears for artifact messages, file downloads
- Artifacts panel in sidebar lists the session's artifacts
- Sidebar logo is visible and correctly aligned

**Do verify the filter after each OpenWebUI database migration.** The stream filter lives in OpenWebUI's database (Admin → Functions), not in this source repo. An OpenWebUI database reset wipes it — re-paste from `../backend/openwebui/invertix_filter.py`.

---

## 4. Don'ts

**Don't modify OpenWebUI's routing, auth, or session storage logic.** These are the highest-churn areas upstream and the hardest conflicts to resolve. Everything we need (run_id, backend_url, artifacts) goes into `localStorage` under `inv_*` keys — we never touch OpenWebUI's own message/session data model.

**Don't add state to existing upstream stores** (`chatStore`, `settings`, etc.). Create your own store file instead.

**Don't remove upstream features by deleting large blocks** if you can help it. Comment them out with a `// Invertix: disabled —` note so the intent is clear and the code can be restored easily. Exception: if the removed block causes an import error or runtime crash, delete it and note the removal in `CHANGES.md`.

**Don't put business logic in upstream component files.** If a feature needs logic, put it in a new store or a new component. The upstream file should only hold a one-line call into your code.

**Don't upgrade OpenWebUI during an active sprint.** Pick a quiet window, allocate half a day, and treat the upgrade as its own PR.

**Don't skip the filter re-paste after an upgrade.** The filter is not in source control — it's the most commonly forgotten step after an upgrade or database restore.

**Don't hardcode client-specific values** (logo path, colour hex, backend URL) inside upstream component files. Use CSS variables or environment variables so a second deployment can swap them without touching the same files again.

---

## 5. How to Upgrade to a New Upstream Version

Follow this sequence exactly. Do not skip steps.

### Step 1 — Check the upstream changelog
Go to `https://github.com/open-webui/open-webui/releases` and read the release notes for every version between your current base and the target. Flag any changes to the Red files listed in Section 2.

### Step 2 — Create an upgrade branch
```bash
git checkout -b upgrade/owui-X.Y.Z
```

### Step 3 — Add upstream as a remote (first time only)
```bash
git remote add upstream https://github.com/open-webui/open-webui.git
git fetch upstream
```

### Step 4 — Merge upstream tag
```bash
git merge upstream/vX.Y.Z --no-commit --no-ff
```
The `--no-commit` flag lets you review conflicts before they land.

### Step 5 — Resolve conflicts in priority order
1. **Green files** — no conflicts expected; if any, upstream added a file with the same name (rename ours).
2. **Yellow files** — conflicts are small; re-apply our one-liners on top of the new upstream version.
3. **Red files** — open each file in a diff tool. Accept upstream's new code, then re-apply our additions on top. Use `CHANGES.md` as the reference for exactly what we added and where.

### Step 6 — Run the app locally
```bash
npm install   # in case package.json changed
npm run dev
```
Walk through the golden path test list from Section 3.

### Step 7 — Update `CHANGES.md`
Update the "Forked from" version line at the top and note any lines that shifted due to the merge.

### Step 8 — Commit and PR
```bash
git add <specific files>
git commit -m "chore: upgrade OpenWebUI base to vX.Y.Z"
```
Open a PR, get a review, then merge to `main`.

### Step 9 — Re-paste the filter
After deployment, go to OpenWebUI Admin → Functions and re-paste `../backend/openwebui/invertix_filter.py`. The database may have been reset during the upgrade.

---

## 6. Adding a New Customisation Safely

Before writing any code, answer these questions:

| Question | If yes → |
|---|---|
| Can this be done with a new component file only? | Do it. No upstream file touched. |
| Does the new component need to receive an event from an upstream component? | Add one import + one event handler line to the upstream file. Document in CHANGES.md. |
| Does the new component need to trigger something in a different part of the UI? | Create a new Svelte store. Both components read/write the store. |
| Does this require changing upstream routing, auth, or session logic? | Stop. Find another way. If truly unavoidable, raise it for architectural review first. |

---

## 7. Multi-Deployment Checklist (Office UI Fork)

When forking for a new client deployment, these are the only things that should change between deployments. Everything else is shared code.

- [ ] `static/<client>-full-logo.png` — sidebar logo (replace Enerparc logo)
- [ ] `static/<client>-logo.png` — compact logo
- [ ] `src/lib/components/layout/Sidebar.svelte` — update logo `src` path (one line)
- [ ] `src/app.html` — update `<title>` to client app name
- [ ] `src/lib/constants.ts` — update `APP_NAME`
- [ ] `src/routes/+layout.svelte` — update notification strings (3 lines)
- [ ] `.env` — set `VITE_INVERTIX_BACKEND` to the client's Railway backend URL
- [ ] OpenWebUI Admin → Functions — paste the stream filter
- [ ] OpenWebUI Admin → Settings — set backend URL, model name, branding

Colour palette changes (if the new client has different brand colours) are isolated to:
- `src/lib/components/chat/Messages/EmojiRatingPopup.svelte` — selected state bg + focus ring
- `src/lib/components/chat/MessageInput/InputMenu.svelte` — artifact type icon colours
- `src/lib/components/layout/Sidebar.svelte` — artifact icon colours

All three files use inline hex values — search for `#003877`, `#73B2F2`, `#65B5E2` and replace with the new client palette.
