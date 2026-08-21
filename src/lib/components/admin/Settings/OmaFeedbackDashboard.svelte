<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        OmaFeedbackDashboard.svelte
	// Description: Admin "Feedback Dashboard" — two tabs: Survey (Create Survey,
	//              Ongoing Survey, Survey results) and Feedback (voluntary feedback
	//              results). Data is served by an S3-backed backend managed
	//              separately (see OPEN POINTs); this is the UI shell.
	// Author:      Vasu Chukka
	// ---------------------------------------------------------------------------
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	type Tab = 'survey' | 'feedback';
	let activeTab: Tab = 'survey';

	// OPEN POINT: wire to the S3-backed admin endpoints (managed separately):
	//   - GET  feedback results   → feedbackResults
	//   - GET  ongoing survey      → ongoingSurvey
	//   - GET  survey results      → surveyResults
	//   - POST create survey       → createSurvey()
	let feedbackResults: any[] = [];
	let ongoingSurvey: any = null;
	let surveyResults: any[] = [];

	const createSurvey = async () => {
		// OPEN POINT: open a create-survey flow / POST to the survey endpoint.
		toast.info($i18n.t('Create-survey flow not configured yet.'));
	};

	const tabButtonClass = (active: boolean) =>
		`px-2.5 py-1 text-xs rounded-lg transition ${
			active
				? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
				: 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
		}`;

	const sectionHeadingClass =
		'text-[0.8125rem] font-medium text-gray-900 dark:text-white';
	const emptyClass =
		'flex h-28 flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-gray-100/70 text-center text-xs text-gray-400 dark:border-white/[0.06] dark:text-gray-600';
</script>

<div class="flex flex-col h-full text-sm">
	<h2 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">
		{$i18n.t('Feedback Dashboard')}
	</h2>

	<div class="mb-4 flex items-center gap-1">
		<button class={tabButtonClass(activeTab === 'survey')} on:click={() => (activeTab = 'survey')}>
			{$i18n.t('Survey')}
		</button>
		<button class={tabButtonClass(activeTab === 'feedback')} on:click={() => (activeTab = 'feedback')}>
			{$i18n.t('Feedback')}
		</button>
	</div>

	<div class="flex-1 min-h-0 overflow-y-auto scrollbar-hover pr-1.5">
		{#if activeTab === 'survey'}
			<div class="flex flex-col gap-5">
				<!-- Create Survey -->
				<section class="flex flex-col gap-2">
					<div class="flex items-center justify-between gap-2">
						<div class={sectionHeadingClass}>{$i18n.t('Create Survey')}</div>
						<button
							class="rounded-full bg-[#003877] px-3 py-1.5 text-xs font-medium text-white transition hover:bg-[#002a63]"
							type="button"
							on:click={createSurvey}
						>
							{$i18n.t('Create survey')}
						</button>
					</div>
					<p class="text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('Configure and launch a new survey for users.')}
					</p>
				</section>

				<!-- Ongoing Survey -->
				<section class="flex flex-col gap-2">
					<div class={sectionHeadingClass}>{$i18n.t('Ongoing Survey')}</div>
					{#if !ongoingSurvey}
						<div class={emptyClass}>
							<div>{$i18n.t('No ongoing survey.')}</div>
							<div>{$i18n.t('The currently running survey will appear here.')}</div>
						</div>
					{:else}
						<div class="rounded-xl border border-gray-100/60 p-3 dark:border-white/[0.05]">
							<div class="text-sm text-gray-800 dark:text-gray-200">{ongoingSurvey?.title}</div>
						</div>
					{/if}
				</section>

				<!-- Survey results -->
				<section class="flex flex-col gap-2">
					<div class={sectionHeadingClass}>{$i18n.t('Survey results')}</div>
					{#if surveyResults.length === 0}
						<div class={emptyClass}>
							<div>{$i18n.t('No survey results yet.')}</div>
							<div>{$i18n.t('Results from completed surveys will appear here.')}</div>
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
				</section>
			</div>
		{:else if activeTab === 'feedback'}
			<section class="flex flex-col gap-2">
				<div class={sectionHeadingClass}>{$i18n.t('Feedback results')}</div>
				{#if feedbackResults.length === 0}
					<div class={emptyClass}>
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
			</section>
		{/if}
	</div>
</div>
