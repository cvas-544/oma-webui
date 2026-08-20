<!-- ---------------------------------------------------------------------------
File:        OmaSuggestions.svelte
Description: O&M-specific quick-start suggestion prompts for the home page
Author:      Vasu Chukka
Co-author:   Claude Code
--------------------------------------------------------------------------- -->
<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';

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
			<button
				class="flex flex-col text-left px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700
					   bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800
					   transition-colors duration-150 group"
				style="animation-delay: {idx * 60}ms"
				on:click={() => dispatch('select', { type: 'prompt', data: $i18n.t(s.promptKey) })}
			>
				<span
					class="text-sm font-medium text-gray-800 dark:text-gray-100 line-clamp-1
						   group-hover:text-[#003877] dark:group-hover:text-blue-300 transition-colors"
				>
					{$i18n.t(s.titleKey)}
				</span>
				<span class="text-xs text-gray-500 dark:text-gray-400 line-clamp-1 mt-0.5">
					{$i18n.t(s.subtitleKey)}
				</span>
			</button>
		{/each}
	</div>
</div>
