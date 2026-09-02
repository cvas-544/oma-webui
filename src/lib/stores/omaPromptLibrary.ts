// ---------------------------------------------------------------------------
// File:        omaPromptLibrary.ts
// Description: Store to open the OMA Prompt Library modal from anywhere.
//              The modal is mounted once at the app root in +layout.svelte.
// Author:      Vasu Chukka
// Co-author:   Claude Code
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';

export const showOmaPromptLibrary = writable(false);

// When user clicks "Use prompt", this store carries the text to the chat input.
export const omaPromptInsert = writable<string | null>(null);
