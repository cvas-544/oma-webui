<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        OmaFeedbackModal.svelte
	// Description: Voluntary user feedback modal (separate from the periodic
	//              Survey). Opened from the user menu via the showOmaFeedback store.
	//              Backend (S3-backed) is wired separately via VITE_OMA_FEEDBACK_URL.
	// Author:      Vasu Chukka
	// ---------------------------------------------------------------------------
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { user } from '$lib/stores';
	import { showOmaFeedback } from '$lib/stores/omaFeedback';
	import Modal from '$lib/components/common/Modal.svelte';

	const i18n = getContext('i18n');

	const categories = ['bug', 'idea', 'praise', 'other'] as const;
	type Category = (typeof categories)[number];

	let category: Category = 'idea';
	let message = '';
	let submitting = false;

	const reset = () => {
		category = 'idea';
		message = '';
		submitting = false;
	};

	const close = () => {
		showOmaFeedback.set(false);
		reset();
	};

	const submit = async () => {
		if (!message.trim() || submitting) {
			return;
		}
		submitting = true;

		// OPEN POINT: backend that writes to the S3 feedback prefix is managed
		// separately. When VITE_OMA_FEEDBACK_URL is set, POST there; otherwise
		// this is a no-op stub so the UI works end-to-end during development.
		const endpoint = import.meta.env.VITE_OMA_FEEDBACK_URL ?? '';
		const payload = {
			type: 'voluntary',
			category,
			message: message.trim(),
			user_id: $user?.id ?? null,
			user_name: $user?.name ?? null,
			created_at: new Date().toISOString()
		};

		try {
			if (endpoint) {
				await fetch(endpoint, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						authorization: `Bearer ${localStorage.token}`
					},
					body: JSON.stringify(payload)
				});
			} else {
				console.log('[OMA feedback] (stub, no VITE_OMA_FEEDBACK_URL set):', payload);
			}
			toast.success($i18n.t('Thanks for your feedback!'));
			close();
		} catch (error) {
			console.error('OMA feedback submit failed:', error);
			toast.error($i18n.t('Could not send feedback. Please try again.'));
			submitting = false;
		}
	};

	const inputClass =
		'w-full resize-none rounded-lg border border-gray-100/50 bg-gray-50/40 px-3 py-2 text-sm text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';
</script>

<Modal bind:show={$showOmaFeedback} size="sm" on:close={reset}>
	<div class="flex flex-col gap-3 px-4 py-4">
		<div class="flex items-center justify-between">
			<h2 class="text-base font-medium text-gray-900 dark:text-white">
				{$i18n.t('Send feedback')}
			</h2>
			<button
				class="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 dark:hover:bg-gray-800"
				type="button"
				aria-label={$i18n.t('Close')}
				on:click={close}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="size-4"
				>
					<path
						d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"
					/>
				</svg>
			</button>
		</div>

		<p class="text-xs text-gray-500 dark:text-gray-400">
			{$i18n.t('Tell us what’s working or what we can improve. This is optional.')}
		</p>

		<div class="flex flex-col gap-1">
			<span class="text-xs font-medium text-gray-600 dark:text-gray-400">{$i18n.t('Category')}</span>
			<select
				bind:value={category}
				class="w-full rounded-lg border border-gray-100/50 bg-gray-50/40 px-3 py-2 text-sm text-gray-700 outline-hidden transition-colors focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:focus:border-blue-500"
			>
				<option value="bug">{$i18n.t('Bug')}</option>
				<option value="idea">{$i18n.t('Idea')}</option>
				<option value="praise">{$i18n.t('Praise')}</option>
				<option value="other">{$i18n.t('Other')}</option>
			</select>
		</div>

		<div class="flex flex-col gap-1">
			<span class="text-xs font-medium text-gray-600 dark:text-gray-400">{$i18n.t('Message')}</span>
			<textarea
				bind:value={message}
				rows="4"
				class={inputClass}
				placeholder={$i18n.t('Share your feedback…')}
			/>
		</div>

		<div class="flex justify-end gap-2 pt-1">
			<button
				class="rounded-full px-3.5 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
				type="button"
				on:click={close}
			>
				{$i18n.t('Cancel')}
			</button>
			<button
				class="rounded-full bg-[#003877] px-3.5 py-1.5 text-sm font-medium text-white transition hover:bg-[#002a63] disabled:opacity-50"
				type="button"
				disabled={!message.trim() || submitting}
				on:click={submit}
			>
				{submitting ? $i18n.t('Sending…') : $i18n.t('Send')}
			</button>
		</div>
	</div>
</Modal>
