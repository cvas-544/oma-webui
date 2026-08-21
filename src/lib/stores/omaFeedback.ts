// ---------------------------------------------------------------------------
// File:        omaFeedback.ts
// Description: Store to open the voluntary OMA feedback modal from anywhere
//              (e.g. the user menu). The modal is mounted once at the app root.
// Author:      Vasu Chukka
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';

// Set true to open the voluntary feedback modal; the modal resets it on close.
export const showOmaFeedback = writable(false);
