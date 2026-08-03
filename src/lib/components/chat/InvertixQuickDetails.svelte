<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        InvertixQuickDetails.svelte
	// Description: Card shown above the chat input when the Invertix agent emits
	//              <!--ASK:--> tags. Groups questions with numbered option pickers.
	//              Renders only when pendingAskGroups has items.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------

	export let groups: { question: string; options: string[] }[] = [];
	export let onSubmit: (text: string) => void = () => {};
	export let onDismiss: () => void = () => {};

	// selections[i] = selected option text for group i (null = nothing picked yet)
	let selections: (string | null)[] = groups.map(() => null);

	$: allSelected = selections.every((s) => s !== null);

	function select(groupIdx: number, option: string) {
		selections[groupIdx] = option;
		selections = [...selections]; // trigger reactivity
	}

	function handleSend() {
		if (!allSelected) return;
		const text = selections.filter(Boolean).join(', ');
		onSubmit(text);
	}

	function handleOptionKey(e: KeyboardEvent, groupIdx: number, option: string) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			select(groupIdx, option);
		}
	}
</script>

<div
	class="mx-auto mb-2 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg overflow-hidden w-[64%]"
	role="dialog"
	aria-label="Quick details"
>
	<!-- Header -->
	<div class="flex items-center justify-between px-4 py-2.5">
		<span class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">A few quick details</span>
		<button
			class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition rounded-full p-0.5"
			on:click={onDismiss}
			aria-label="Dismiss"
		>
			<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<line x1="18" y1="6" x2="6" y2="18" />
				<line x1="6" y1="6" x2="18" y2="18" />
			</svg>
		</button>
	</div>

	<!-- Groups — scrollable if many questions -->
	<div class="overflow-y-auto max-h-[18.4rem]">
		{#each groups as group, gi}
			<div class="border-t border-gray-100 dark:border-gray-800 px-4 py-2">
				<div class="text-xs text-gray-500 dark:text-gray-400 mb-1.5">{group.question}</div>
				<div class="flex flex-col gap-0.5">
					{#each group.options as option, oi}
						{@const selected = selections[gi] === option}
						<button
							class="flex items-center gap-2.5 py-1.5 px-2 rounded-xl text-left transition
								{selected
									? 'dark:bg-gray-100'
									: 'hover:bg-gray-50 dark:hover:bg-gray-800'}"
						style={selected ? 'background-color: #003877;' : ''}
							on:click={() => select(gi, option)}
							on:keydown={(e) => handleOptionKey(e, gi, option)}
							aria-pressed={selected}
						>
							<span
								class="flex-shrink-0 w-5 h-5 rounded-full text-xs font-medium flex items-center justify-center transition
									{selected
										? 'bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100'
										: 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'}"
							>
								{oi + 1}
							</span>
							<span
								class="text-sm font-medium transition
									{selected ? 'text-white dark:text-gray-900' : 'text-gray-800 dark:text-gray-200'}"
							>
								{option}
							</span>
						</button>
					{/each}
				</div>
			</div>
		{/each}
	</div>

	<!-- Footer: Send + hint -->
	<div class="border-t border-gray-100 dark:border-gray-800 px-4 py-3 flex flex-col gap-1.5">
		<button
			class="w-full rounded-full py-2 text-sm font-semibold transition
				{allSelected
					? 'text-white dark:text-white cursor-pointer'
					: 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'}"
			style={allSelected ? 'background-color: #003877;' : ''}
			on:click={handleSend}
			disabled={!allSelected}
		>
			Send ↵
		</button>
		<p class="text-xs text-center text-gray-400 dark:text-gray-500">
			Not listed? Just type what you need below.
		</p>
	</div>
</div>
