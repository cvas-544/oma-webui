<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        InvertixStepsCard.svelte
	// Description: Reasoning step card shown inside the O&M Agent message bubble.
	//              Mirrors the SandboxSection in the Invertix React frontend but
	//              uses #73B2F2 (Enerparc blue) instead of orange.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------

	export let steps: { id: string; type: string; tool: string; ts: number; failed: boolean }[] = [];
	export let streaming = false;
	export let responding = false; // true when content has started streaming (last thinking step = "Writing response")

	let open = true;
	$: if (!streaming) open = false;

	$: lastIdx = steps.length - 1;
	$: relabelLast = responding && steps[lastIdx]?.type === 'thinking';

	function stepLabel(step: { type: string; tool: string }): string {
		if (step.type === 'thinking') return 'Thinking';
		if (step.type === 'code_execution') return 'Executing analysis';
		if (step.type === 'tool_result') return 'Retrieved results';
		if (step.type === 'tool_call') {
			const t = step.tool;
			if (t === 'thinking') return 'Thinking';
			if (t === 'read_document') return 'Reading document';
			if (t === 'query_plant_data') return 'Querying plant data';
			if (t === 'execute_code') return 'Executing analysis';
			if (t === 'generate_report') return 'Generating report';
			return `Calling ${t}`;
		}
		return step.type;
	}

	function stepSummary(step: { type: string; tool: string; failed: boolean }): string {
		if (step.type === 'thinking') return 'Analyzed the request and planned the best approach.';
		if (step.type === 'code_execution') return 'Prepared Python code in the analysis environment.';
		if (step.type === 'tool_result') {
			return step.failed
				? 'Tool returned an error; agent retrying.'
				: 'Retrieved results from the tool.';
		}
		if (step.type === 'tool_call') {
			const t = step.tool;
			if (t === 'query_plant_data') return 'Queried plant data from the database.';
			if (t === 'generate_report') return 'Building report in the E2B sandbox.';
			if (t === 'execute_code') return 'Executed Python code in the sandboxed analysis environment.';
			if (t === 'read_document') return 'Read the existing report to edit it.';
			return `Invoked the ${t} tool.`;
		}
		return '';
	}

	function runningTitle(steps: { type: string; tool: string }[]): string {
		for (let i = steps.length - 1; i >= 0; i--) {
			const s = steps[i];
			if (s.type === 'thinking') return 'Thinking';
			if (s.type === 'code_execution') return 'Executing analysis';
			if (s.type === 'tool_call') {
				if (s.tool === 'query_plant_data') return 'Querying data';
				if (s.tool === 'generate_report') return 'Generating report';
				if (s.tool === 'execute_code') return 'Executing analysis';
				if (s.tool === 'read_document') return 'Reading document';
			}
		}
		return 'Working on it';
	}

	function doneTitle(steps: { type: string; tool: string }[]): string {
		const hasDoc = steps.some(
			(s) => s.type === 'tool_call' && s.tool === 'generate_report'
		);
		if (hasDoc) return 'Report generated';
		const analyzed = steps.some(
			(s) =>
				s.type === 'tool_call' &&
				(s.tool === 'query_plant_data' || s.tool === 'execute_code')
		);
		return analyzed ? 'Analysis complete' : 'Response ready';
	}

	function fmtDuration(ms: number): string {
		if (ms <= 0) return '';
		return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
	}

	$: title = streaming
		? relabelLast
			? 'Writing response'
			: runningTitle(steps)
		: doneTitle(steps);
</script>

{#if steps.length > 0}
	<div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-850 overflow-hidden mb-3" style="margin-top: 8px;">
		<!-- Header -->
		<button
			class="w-full flex items-center justify-between px-3.5 py-2.5 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left"
			on:click={() => (open = !open)}
		>
			<div class="flex items-center gap-2 min-w-0">
				<!-- Activity / heartbeat icon -->
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-3.5 h-3.5 shrink-0"
					viewBox="0 0 24 24"
					fill="none"
					stroke="#73B2F2"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
				</svg>

				<span class="text-[13px] font-medium text-gray-800 dark:text-gray-100">{title}</span>
				<span class="text-[11px] text-gray-400 dark:text-gray-500 ml-1">
					{streaming ? `${steps.length} steps…` : `${steps.length} steps`}
				</span>

				{#if streaming}
					<span
						class="w-1.5 h-1.5 rounded-full shrink-0 animate-pulse"
						style="background-color: #73B2F2;"
					></span>
				{/if}
			</div>

			<!-- Chevron -->
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="w-3.5 h-3.5 text-gray-400 shrink-0 transition-transform {open ? 'rotate-180' : ''}"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
			>
				<polyline points="6 9 12 15 18 9" />
			</svg>
		</button>

		<!-- Steps list -->
		{#if open}
			<div class="px-3.5 pb-3 pt-2 border-t border-gray-100 dark:border-gray-700 space-y-0">
				{#each steps as step, i}
					{@const isLast = i === steps.length - 1}
					{@const isActive = streaming && isLast}
					{@const isWriting = relabelLast && isLast}
					{@const nextTs = steps[i + 1]?.ts}
					{@const durationMs = nextTs && step.ts ? nextTs - step.ts : undefined}
					{@const label = isWriting ? 'Writing response' : stepLabel(step)}
					{@const summary = isWriting ? 'Composing the final answer.' : stepSummary(step)}

					<div class="flex gap-1.5">
						<!-- Badge + connector column -->
						<div class="flex flex-col items-center shrink-0">
							{#if isActive}
								<!-- Spinning blue circle -->
								<span
									class="inline-flex items-center justify-center w-4 h-4 rounded-full"
									style="background-color: rgba(115,178,242,0.15);"
								>
									<svg
										class="w-3 h-3 animate-spin"
										style="color: #73B2F2;"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
									>
										<circle
											class="opacity-25"
											cx="12"
											cy="12"
											r="10"
											stroke="currentColor"
											stroke-width="4"
										/>
										<path
											class="opacity-75"
											fill="currentColor"
											d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
										/>
									</svg>
								</span>
							{:else if step.failed}
								<!-- Grey X -->
								<span
									class="inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-400"
								>
									<svg
										class="w-2.5 h-2.5 text-white"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
										stroke-width="3"
									>
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								</span>
							{:else}
								<!-- Blue check -->
								<span
									class="inline-flex items-center justify-center w-4 h-4 rounded-full"
									style="background-color: #73B2F2;"
								>
									<svg
										class="w-2.5 h-2.5 text-white"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
										stroke-width="3"
									>
										<polyline points="20 6 9 17 4 12" />
									</svg>
								</span>
							{/if}

							<!-- Vertical connector -->
							{#if !isLast}
								<div class="w-px flex-1 bg-gray-200 dark:bg-gray-700 my-1" />
							{/if}
						</div>

						<!-- Content column -->
						<div class="flex-1 min-w-0 pb-2">
							<div class="flex items-center gap-1.5 text-[11px] text-gray-500 dark:text-gray-400 flex-wrap">
								<span class="font-medium text-gray-700 dark:text-gray-200">{label}</span>
								{#if step.tool && !isWriting}
									<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 leading-none">{step.tool}</span>
								{/if}
								{#if durationMs != null && durationMs > 0}
									<span class="text-[10px] text-gray-400 dark:text-gray-500 tabular-nums"
										>{fmtDuration(durationMs)}</span
									>
								{/if}
							</div>
							{#if summary}
								<p class="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 leading-snug">
									{summary}
								</p>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}
