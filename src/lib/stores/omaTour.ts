// ---------------------------------------------------------------------------
// File:        omaTour.ts
// Description: Store to trigger the OMA quick tour guide from anywhere.
// Author:      Vasu Chukka
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';

export const showOmaTour = writable(false);
