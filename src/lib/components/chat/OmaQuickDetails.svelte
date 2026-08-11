<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        OmaQuickDetails.svelte
	// Description: Stepped question picker shown above the chat input when the
	//              OMA agent emits ask-back tags. One question per step with
	//              live search filter, free-text fallback, back/next navigation,
	//              dot-progress indicator, and a Submit that activates only when
	//              every step has an answer.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------

	import { fly } from 'svelte/transition';

	export let groups: { question: string; options: string[] }[] = [];
	export let onSubmit: (text: string) => void = () => {};
	export let onDismiss: () => void = () => {};

	let direction = 1; // 1 = forward (slide left), -1 = back (slide right)

	// Enerparc brand palette
	const EP_DARK  = '#003877';
	const EP_LIGHT = '#65B5E2';
	const EP_MUTED = '#D0DFF0';
	const EP_TEXT  = '#3D6D88';

	let step = 0;
	let selections: (string | null)[] = groups.map(() => null);
	let customTexts: string[] = groups.map(() => '');
	let searchQuery = '';
	let bodyHeight = 0;

	$: total = groups.length;
	$: currentGroup = groups[step] ?? { question: '', options: [] };
	$: isFirst = step === 0;
	$: isLast  = step === total - 1;
	$: allAnswered = selections.every((s) => s !== null && (s as string).trim() !== '');
	$: currentPick = selections[step];
	$: filteredOptions = currentGroup.options.filter((o) =>
		searchQuery.trim() === ''
			? true
			: o.toLowerCase().includes(searchQuery.toLowerCase())
	);

	function jumpTo(s: number) {
		direction = s > step ? 1 : -1;
		step = s;
		searchQuery = '';
	}

	function goBack()  { if (!isFirst) jumpTo(step - 1); }
	function goNext()  { if (!isLast)  jumpTo(step + 1); }

	function pickOption(option: string) {
		selections[step] = option;
		customTexts[step] = '';
		selections = [...selections];
		if (!isLast) setTimeout(goNext, 160);
	}

	function handleCustomInput(e: Event) {
		const val = (e.target as HTMLInputElement).value;
		customTexts[step] = val;
		selections[step] = val.trim() ? val.trim() : null;
		selections = [...selections];
	}

	function handleCustomKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !isLast && selections[step]) goNext();
	}

	function handleSearchKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && filteredOptions.length === 1) pickOption(filteredOptions[0]);
		if (e.key === 'Escape') searchQuery = '';
	}

	function handleOptionKey(e: KeyboardEvent, option: string) {
		if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pickOption(option); }
	}

	function handleSubmit() {
		if (!allAnswered) return;
		const text = groups.map((g, i) => `${g.question}: ${selections[i]}`).join('\n');
		onSubmit(text);
	}

	$: dotStyles = groups.map((_, i) => {
		if (selections[i])  return `background-color:${EP_DARK};width:${i===step?'18px':'6px'};height:6px;border-radius:9999px;transition:all 0.2s;`;
		if (i === step)     return `background-color:${EP_LIGHT};width:18px;height:6px;border-radius:9999px;transition:all 0.2s;`;
		return `background-color:${EP_MUTED};width:6px;height:6px;border-radius:9999px;transition:all 0.2s;`;
	});
</script>

<div
	class="mb-2 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg overflow-hidden relative"
	role="dialog"
	aria-label="Quick details"
>
	<!-- ── Header ── -->
	<div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
		<span class="text-sm font-medium text-gray-500 dark:text-gray-400">A few quick details</span>

		<div class="flex items-center gap-3">
			<!-- Step counter -->
			<span class="text-xs font-semibold tabular-nums" style="color:{EP_DARK};">
				{step + 1} / {total}
			</span>
			<!-- Dismiss -->
			<button
				class="p-0.5 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition"
				on:click={onDismiss}
				aria-label="Dismiss"
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<line x1="18" y1="6" x2="6" y2="18" />
					<line x1="6" y1="6" x2="18" y2="18" />
				</svg>
			</button>
		</div>
	</div>

	<!-- ── Previous answers (clickable chips) ── -->
	{#if step > 0}
		<div class="px-5 pt-3 pb-0 flex flex-wrap gap-1.5">
			{#each groups.slice(0, step) as g, i}
				{#if selections[i]}
					<button
						class="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition"
						on:click={() => jumpTo(i)}
						title="Click to change"
					>
						<span class="text-gray-400">{g.question.replace(/[?？]$/, '')}:</span>
						<span class="font-medium text-gray-700 dark:text-gray-200 max-w-[130px] truncate">{selections[i]}</span>
					</button>
				{/if}
			{/each}
		</div>
	{/if}

	<!-- ── Question body ── -->
	<div class="relative overflow-hidden" style="min-height:{bodyHeight}px">
	{#key step}
	<div
		class="px-5 pt-3.5 pb-4 w-full"
		bind:clientHeight={bodyHeight}
		in:fly={{ x: direction * 48, duration: 220, opacity: 0 }}
		out:fly|local={{ x: direction * -48, duration: 180, opacity: 0 }}
		style="position: absolute; left:0; right:0; top:0;"
	>
		<p class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3">{currentGroup.question}</p>

		{#if currentGroup.options.length > 0}
			<!-- Search -->
			<div class="relative mb-2.5">
				<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
					<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
					</svg>
				</div>
				<input
					type="text"
					placeholder="Filter options…"
					class="w-full pl-8 pr-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:border-gray-400 dark:focus:border-gray-500 transition"
					bind:value={searchQuery}
					on:keydown={handleSearchKey}
				/>
			</div>

			<!-- Options list -->
			<div class="flex flex-col gap-0.5 max-h-48 overflow-y-auto" role="listbox">
				{#if filteredOptions.length === 0}
					<p class="text-xs text-center text-gray-400 dark:text-gray-500 py-3">No match — type your own below</p>
				{:else}
					{#each filteredOptions as option, oi}
						{@const selected = currentPick === option}
						<button
							class="flex items-center gap-3 py-2 px-2 rounded-xl text-left transition
								{selected ? '' : 'hover:bg-gray-50 dark:hover:bg-gray-800'}"
							style={selected ? `background-color:${EP_DARK};` : ''}
							on:click={() => pickOption(option)}
							on:keydown={(e) => handleOptionKey(e, option)}
							role="option"
							aria-selected={selected}
						>
							<span
								class="flex-shrink-0 w-6 h-6 rounded-full text-xs font-medium flex items-center justify-center transition
									{selected ? '' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'}"
								style={selected ? 'background-color:rgba(255,255,255,0.18);color:white;' : ''}
							>
								{oi + 1}
							</span>
							<span
								class="text-sm font-medium transition {selected ? '' : 'text-gray-800 dark:text-gray-200'}"
								style={selected ? 'color:white;' : ''}
							>
								{option}
							</span>
						</button>
					{/each}
				{/if}
			</div>
		{/if}

		<!-- Free-text fallback -->
		<div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
			<p class="text-xs text-gray-400 dark:text-gray-500 mb-1.5">Or type your own answer</p>
			<input
				type="text"
				placeholder="Type here…"
				class="w-full px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:border-gray-400 dark:focus:border-gray-500 transition"
				value={customTexts[step]}
				on:input={handleCustomInput}
				on:keydown={handleCustomKey}
			/>
		</div>
	</div>
	{/key}
	</div>

	<!-- ── Footer ── -->
	<div class="border-t border-gray-100 dark:border-gray-800 px-5 py-3 flex items-center justify-between gap-3">
		<!-- Dot progress -->
		<div class="flex items-center gap-1.5">
			{#each groups as _, i}
				<div style={dotStyles[i]}></div>
			{/each}
		</div>

		<!-- Nav -->
		<div class="flex items-center gap-2">
			{#if !isFirst}
				<button
					class="px-3.5 py-1.5 rounded-xl text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
					on:click={goBack}
				>
					← Back
				</button>
			{/if}

			{#if !isLast}
				<button
					class="px-3.5 py-1.5 rounded-xl text-sm font-semibold transition"
					style="background-color:{currentPick ? EP_DARK : EP_MUTED}; color:{currentPick ? 'white' : EP_TEXT};"
					on:click={goNext}
				>
					Next →
				</button>
			{:else}
				<button
					class="px-4 py-1.5 rounded-xl text-sm font-semibold transition"
					style="background-color:{allAnswered ? EP_DARK : EP_MUTED}; color:{allAnswered ? 'white' : EP_TEXT}; cursor:{allAnswered ? 'pointer' : 'not-allowed'};"
					on:click={handleSubmit}
					disabled={!allAnswered}
				>
					Submit
				</button>
			{/if}
		</div>
	</div>
</div>
