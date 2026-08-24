// ---------------------------------------------------------------------------
// File:        omaHelp.ts
// Description: Store to open the OMA Help / ticket modal from anywhere.
//              The modal is mounted once at the app root.
// Author:      Vasu Chukka
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';

export const showOmaHelp = writable(false);
