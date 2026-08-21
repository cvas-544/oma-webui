// ---------------------------------------------------------------------------
// File:        omaVersion.ts
// Description: OMA agent + UI version strings, sourced from build-time env vars.
//              Displayed in Settings → About for all users.
// Author:      Vasu Chukka
// ---------------------------------------------------------------------------

// OMA: version values come from build-time env vars for now.
// OPEN POINT: wire the UI version to a git tag via `git describe --tags` (Vite
// define) and/or fetch the agent version at runtime from the shim. See docs.
export const OMA_AGENT_VERSION: string = import.meta.env.VITE_OMA_AGENT_VERSION ?? '';
export const OMA_UI_VERSION: string = import.meta.env.VITE_OMA_UI_VERSION ?? '';
