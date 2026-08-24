<!-- ---------------------------------------------------------------------------
File:        OmaSuggestions.svelte
Description: O&M-specific quick-start suggestion prompts for the home page
Author:      Vasu Chukka
Co-author:   Claude Code
--------------------------------------------------------------------------- -->
<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';
	import PencilSquare from '$lib/components/icons/PencilSquare.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	type Suggestion = { titleKey: string; subtitleKey: string; promptKey: string };

	const suggestions: Suggestion[] = [
		{
			titleKey: "Yesterday's generation report",
			subtitleKey: 'Energy & performance summary',
			promptKey: 'Show me the generation report for yesterday across all plants.'
		},
		{
			titleKey: 'Active alarms',
			subtitleKey: 'Current fault overview',
			promptKey: 'List all active alarms across my plants right now.'
		},
		{
			titleKey: 'Performance ratio this week',
			subtitleKey: 'Weekly KPI snapshot',
			promptKey: 'What is the performance ratio for each plant this week?'
		},
		{
			titleKey: 'Inverter downtime',
			subtitleKey: 'Availability & losses',
			promptKey:
				'Which inverters had downtime in the last 7 days and what were the energy losses?'
		}
	];
</script>

<div class="flex flex-col gap-2 w-full">
	<div class="grid grid-cols-2 gap-2">
		{#each suggestions as s, idx}
			<div
				class="relative flex flex-col text-left px-2.5 py-2 rounded-xl border border-gray-200 dark:border-gray-700
					   bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800
					   transition-colors duration-150 group cursor-pointer"
				style="animation-delay: {idx * 60}ms"
				role="button"
				tabindex="0"
				on:click={() => dispatch('select', { type: 'prompt', data: $i18n.t(s.promptKey) })}
				on:keydown={(e) => e.key === 'Enter' && dispatch('select', { type: 'prompt', data: $i18n.t(s.promptKey) })}
			>
				<span
					class="text-xs font-medium text-gray-800 dark:text-gray-100 line-clamp-1
						   group-hover:text-[#003877] dark:group-hover:text-blue-300 transition-colors pr-6"
				>
					{$i18n.t(s.titleKey)}
				</span>
				<span class="text-[0.7rem] text-gray-500 dark:text-gray-400 line-clamp-1 mt-0.5">
					{$i18n.t(s.subtitleKey)}
				</span>

				<!-- Edit button — loads prompt into input without submitting -->
				<button
					type="button"
					class="absolute bottom-1.5 right-1.5 flex size-5 items-center justify-center rounded-md
						   text-gray-300 opacity-0 group-hover:opacity-100 hover:!text-gray-600
						   dark:text-gray-600 dark:hover:!text-gray-300 transition-all"
					on:click|stopPropagation={() => dispatch('select', { type: 'prompt-edit', data: $i18n.t(s.promptKey) })}
					aria-label="Edit prompt"
				>
					<PencilSquare className="size-3.5" strokeWidth="1.75" />
				</button>
			</div>
		{/each}
	</div>

</div>
