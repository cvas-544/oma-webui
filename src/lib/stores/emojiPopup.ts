// ---------------------------------------------------------------------------
// File:        emojiPopup.ts
// Description: Global store for the emoji feedback popup. Allows ResponseMessage
//              to open it while Chat.svelte renders it at the top level,
//              avoiding fixed-position stacking-context issues.
// Author:      Vasu Chukka
// Co-author:   Claude Code
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';

export type EmojiPopupState = {
	show: boolean;
	onSubmit: (data: { rating: string; feedback: string; reasons: string[] }) => Promise<void>;
};

function createEmojiPopupStore() {
	const { subscribe, set, update } = writable<EmojiPopupState>({
		show: false,
		onSubmit: async () => {}
	});

	return {
		subscribe,
		open(onSubmit: EmojiPopupState['onSubmit']) {
			set({ show: true, onSubmit });
		},
		close() {
			update((s) => ({ ...s, show: false }));
		}
	};
}

export const emojiPopup = createEmojiPopupStore();
