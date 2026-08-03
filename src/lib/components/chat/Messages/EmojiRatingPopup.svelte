<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        EmojiRatingPopup.svelte
	// Description: Emoji feedback popup shown above the input field after
	//              the user clicks thumbs up / thumbs down on an agent message.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------
	import { fly, fade } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { tick } from 'svelte';

	export let show = false;
	export let onSubmit: (data: { rating: string; feedback: string }) => void = () => {};
	export let onDismiss: () => void = () => {};

	const EMOJIS = [
		{
			id: 'very-sad',
			label: 'Terrible',
			svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10"/>
				<path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
				<path d="M9 9h.01"/><path d="M15 9h.01"/>
				<path d="M9 13v2" stroke="#73B2F2"/><path d="M15 13v2" stroke="#73B2F2"/>
			</svg>`
		},
		{
			id: 'sad',
			label: 'Bad',
			svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10"/>
				<path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
				<path d="M9 9h.01"/><path d="M15 9h.01"/>
			</svg>`
		},
		{
			id: 'neutral',
			label: 'Okay',
			svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10"/>
				<path d="M8 15h8"/>
				<path d="M9 9h.01"/><path d="M15 9h.01"/>
			</svg>`
		},
		{
			id: 'happy',
			label: 'Amazing',
			svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10"/>
				<path d="M8 13s1.5 2 4 2 4-2 4-2"/>
				<path d="M9 9l.5 1.5 1.5.5-1.5.5-.5 1.5-.5-1.5-1.5-.5 1.5-.5z" fill="#65B5E2" stroke="none"/>
				<path d="M15 9l.5 1.5 1.5.5-1.5.5-.5 1.5-.5-1.5-1.5-.5 1.5-.5z" fill="#65B5E2" stroke="none"/>
			</svg>`
		}
	];

	const EMOJI_VALUES: Record<string, number> = {
		'very-sad': 1,
		sad: 2,
		neutral: 3,
		happy: 4
	};

	let selected = '';
	let feedback = '';
	let submitting = false;
	let textareaEl: HTMLTextAreaElement;

	$: if (selected && show) {
		tick().then(() => textareaEl?.focus());
	}

	async function handleSubmit() {
		if (submitting) return;
		submitting = true;
		try {
			await onSubmit({ rating: selected, feedback });
		} finally {
			submitting = false;
			resetAndClose();
		}
	}

	function resetAndClose() {
		selected = '';
		feedback = '';
		onDismiss();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') resetAndClose();
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if show}
	<!-- backdrop: transparent, catches outside clicks -->
	<div
		class="fixed inset-0 z-[100]"
		on:click={resetAndClose}
		transition:fade={{ duration: 120 }}
	/>

	<!-- popup: fixed just above the message input bar -->
	<div
		class="fixed bottom-[88px] left-0 right-0 z-[101] flex justify-center px-4 pointer-events-none"
		transition:fly={{ y: 18, duration: 260, easing: cubicOut }}
	>
		<div
			class="pointer-events-auto overflow-hidden border border-zinc-200 bg-white shadow-[0_20px_60px_-12px_rgba(0,0,0,0.16)] transition-[border-radius,width] duration-300 ease-out {selected
				? 'w-full max-w-[440px] rounded-[28px]'
				: 'rounded-full'}"
			on:click|stopPropagation
		>
			<!-- ── top row: label + emoji buttons ─────────────────────────── -->
			<div class="flex items-center justify-between gap-4 px-5 py-3">
				<span class="select-none whitespace-nowrap text-[13px] font-medium text-zinc-500 ml-1">
					How was this response?
				</span>

				<div class="flex items-center gap-0.5 shrink-0">
					{#each EMOJIS as emoji (emoji.id)}
						<button
							title={emoji.label}
							class="relative rounded-full p-2 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-[#73B2F2] {selected === emoji.id
								? 'text-white'
								: 'text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700'}"
							on:click={() => {
								selected = selected === emoji.id ? '' : emoji.id;
							}}
						>
							<div class="relative z-10 flex h-5 w-5 items-center justify-center">
								{@html emoji.svg}
							</div>
							{#if selected === emoji.id}
								<div class="absolute inset-0 rounded-full bg-[#003877]" />
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<!-- ── expanded body (visible after emoji pick) ───────────────── -->
			{#if selected}
				<div
					class="px-5 pb-5"
					transition:fly={{ y: -8, duration: 200, easing: cubicOut }}
				>
					<div class="mb-2 flex items-center justify-between">
						<span class="text-[10px] font-bold uppercase tracking-[0.1em] text-zinc-400">
							Feedback
						</span>
						<span class="text-[11px] text-zinc-400">Optional</span>
					</div>

					<textarea
						bind:this={textareaEl}
						bind:value={feedback}
						placeholder="Tell us more..."
						rows="3"
						class="w-full resize-none rounded-2xl border border-zinc-200 bg-zinc-50 p-3.5 text-[13px] text-zinc-800 leading-relaxed placeholder:text-zinc-400 focus:border-[#73B2F2] focus:outline-none transition-colors"
					/>

					<div class="mt-3 flex items-center justify-between border-t border-zinc-100 pt-3">
						<button
							class="text-[12px] text-zinc-400 hover:text-zinc-600 transition-colors"
							on:click={resetAndClose}
						>
							Skip
						</button>

						<button
							on:click={handleSubmit}
							disabled={submitting}
							class="rounded-xl bg-[#003877] px-5 py-2 text-[13px] font-semibold text-white transition-all hover:bg-[#002a63] active:scale-95 disabled:opacity-40 disabled:pointer-events-none"
						>
							{#if submitting}
								<div class="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin mx-auto" />
							{:else}
								Send
							{/if}
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}
