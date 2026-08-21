<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        OmaFeedbackDashboard.svelte
	// Description: Admin dashboard scaffold for OMA feedback + survey results.
	//              Admins trigger surveys and review voluntary feedback / survey
	//              results here. Data is served by an S3-backed backend managed
	//              separately (see OPEN POINTs); this is the UI shell.
	// Author:      Vasu Chukka
	// ---------------------------------------------------------------------------
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	type Tab = 'feedback' | 'survey';
	let activeTab: Tab = 'feedback';

	// OPEN POINT: wire to the S3-backed admin endpoints (managed separately):
	//   - GET  feedback results   → feedbackResults
	//   - GET  survey results     → surveyResults
	//   - POST trigger survey     → triggerSurvey()
	let feedbackResults: any[] = [];
	let surveyResults: any[] = [];

	const triggerSurvey = async () => {
		// OPEN POINT: POST to the survey-trigger endpoint.
		toast.info($i18n.t('Survey trigger endpoint not configured yet.'));
	};

	const tabButtonClass = (active: boolean) =>
		`px-2.5 py-1 text-xs rounded-lg transition ${
			active
				? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
				: 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
		}`;
</script>

<div class="flex flex-col h-full text-sm">
	<div class="mb-3 flex items-center justify-between gap-2">
		<h2 class="text-sm font-medium text-gray-900 dark:text-white">{$i18n.t('Feedback')}</h2>

		<button
			class="rounded-full bg-[#003877] px-3 py-1.5 text-xs font-medium text-white transition hover:bg-[#002a63]"
			type="button"
			on:click={triggerSurvey}
		>
			{$i18n.t('Trigger survey')}
		</button>
	</div>

	<div class="mb-3 flex items-center gap-1">
		<button class={tabButtonClass(activeTab === 'feedback')} on:click={() => (activeTab = 'feedback')}>
			{$i18n.t('Feedback results')}
		</button>
		<button class={tabButtonClass(activeTab === 'survey')} on:click={() => (activeTab = 'survey')}>
			{$i18n.t('Survey results')}
		</button>
	</div>

	<div class="flex-1 min-h-0 overflow-y-auto scrollbar-hover pr-1.5">
		{#if activeTab === 'feedback'}
			{#if feedbackResults.length === 0}
				<div
					class="flex h-40 flex-col items-center justify-center gap-1 text-center text-xs text-gray-400 dark:text-gray-600"
				>
					<div>{$i18n.t('No feedback yet.')}</div>
					<div>{$i18n.t('Voluntary feedback from users will appear here.')}</div>
				</div>
			{:else}
				<div class="flex flex-col gap-2">
					{#each feedbackResults as item}
						<div class="rounded-xl border border-gray-100/60 p-3 dark:border-white/[0.05]">
							<div class="text-xs text-gray-500 dark:text-gray-400">
								{item?.category} · {item?.user_name} · {item?.created_at}
							</div>
							<div class="mt-1 text-sm text-gray-800 dark:text-gray-200">{item?.message}</div>
						</div>
					{/each}
				</div>
			{/if}
		{:else if activeTab === 'survey'}
			{#if surveyResults.length === 0}
				<div
					class="flex h-40 flex-col items-center justify-center gap-1 text-center text-xs text-gray-400 dark:text-gray-600"
				>
					<div>{$i18n.t('No survey results yet.')}</div>
					<div>{$i18n.t('Trigger a survey to start collecting responses.')}</div>
				</div>
			{:else}
				<div class="flex flex-col gap-2">
					{#each surveyResults as item}
						<div class="rounded-xl border border-gray-100/60 p-3 dark:border-white/[0.05]">
							<div class="text-sm text-gray-800 dark:text-gray-200">{JSON.stringify(item)}</div>
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	</div>
</div>
