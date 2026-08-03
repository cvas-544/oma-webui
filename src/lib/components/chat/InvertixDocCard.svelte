<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        InvertixDocCard.svelte
	// Description: Download card shown above the chat input when the Invertix
	//              agent finishes generating a PDF or Excel report. Emits
	//              invertix:doc_ready events consumed by Chat.svelte.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------

	export let docs: { name: string; url: string; ext: string }[] = [];
	export let onDismissAll: () => void = () => {};
</script>

{#if docs.length > 0}
	<div class="mb-2 flex flex-col gap-2">
		{#each docs as doc}
			<div
				class="flex items-center gap-3 px-4 py-3 rounded-2xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
			>
				<!-- File icon -->
				<div class="flex-shrink-0 text-gray-400 dark:text-gray-500">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-8 h-8"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
						<line x1="3" y1="9" x2="21" y2="9" />
						<line x1="3" y1="15" x2="21" y2="15" />
						<line x1="9" y1="9" x2="9" y2="21" />
					</svg>
				</div>

				<!-- Name + ext -->
				<div class="flex-1 min-w-0">
					<p class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">{doc.name}</p>
					<p class="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{doc.ext}</p>
				</div>

				<!-- Download button -->
				<a
					href={doc.url}
					download={doc.name}
					class="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-white text-sm font-semibold transition" style="background-color: #003877;" on:mouseenter={(e) => e.currentTarget.style.backgroundColor='#002a63'} on:mouseleave={(e) => e.currentTarget.style.backgroundColor='#003877'}
					on:click={onDismissAll}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-4 h-4"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
						<polyline points="7 10 12 15 17 10" />
						<line x1="12" y1="15" x2="12" y2="3" />
					</svg>
					Download
				</a>
			</div>
		{/each}
	</div>
{/if}
