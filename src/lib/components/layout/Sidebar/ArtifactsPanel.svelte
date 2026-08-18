<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        ArtifactsPanel.svelte
	// Description: Sidebar panel listing user-generated artifacts (docs + images)
	//              with download and delete actions.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------
	import { artifacts, loadImageBlob } from '$lib/stores/artifacts';
	import { toast } from 'svelte-sonner';

	export let show = false;

	function formatDate(ts: number): string {
		const d = new Date(ts);
		return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function extIcon(ext: string | undefined): string {
		if (!ext) return '📄';
		const e = ext.toLowerCase();
		if (e === 'pdf') return '📕';
		if (e === 'xlsx' || e === 'xls') return '📗';
		return '📄';
	}

	async function downloadDoc(item: { url?: string; name: string }) {
		if (!item.url) return;
		const a = document.createElement('a');
		a.href = item.url;
		a.download = item.name;
		a.target = '_blank';
		a.click();
	}

	async function downloadImage(id: string, name: string) {
		const dataUrl = await loadImageBlob(id);
		if (!dataUrl) {
			toast.error('Image data no longer available.');
			return;
		}
		const a = document.createElement('a');
		a.href = dataUrl;
		a.download = name;
		a.click();
	}

	function handleDelete(id: string) {
		artifacts.remove(id);
	}
</script>

{#if show}
	<div class="flex flex-col h-full overflow-hidden">
		<!-- Header -->
		<div class="flex items-center justify-between px-3 py-2.5 border-b border-gray-100 dark:border-gray-800 shrink-0">
			<span class="text-sm font-semibold text-gray-700 dark:text-gray-200">Artifacts</span>
			<button
				class="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition"
				on:click={() => (show = false)}
				aria-label="Close artifacts panel"
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- List -->
		<div class="flex-1 overflow-y-auto px-2 py-2 space-y-1">
			{#if $artifacts.length === 0}
				<div class="flex flex-col items-center justify-center h-40 text-gray-400 dark:text-gray-600 text-xs gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" class="size-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
					</svg>
					<span>No artifacts yet</span>
				</div>
			{:else}
				{#each $artifacts as item (item.id)}
					<div class="group flex items-center gap-2 rounded-xl px-2.5 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition">
						<!-- Icon -->
						<div class="shrink-0 text-base leading-none">
							{#if item.type === 'image'}
								<svg xmlns="http://www.w3.org/2000/svg" class="size-4 text-[#73B2F2]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							{:else if item.ext === 'pdf'}
								<svg xmlns="http://www.w3.org/2000/svg" class="size-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" class="size-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							{/if}
						</div>

						<!-- Name + date -->
						<div class="flex-1 min-w-0">
							<p class="text-xs font-medium text-gray-700 dark:text-gray-200 truncate">{item.name}</p>
							<p class="text-[10px] text-gray-400 dark:text-gray-500">{formatDate(item.ts)}</p>
						</div>

						<!-- Actions (visible on hover) -->
						<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition shrink-0">
							<!-- Download -->
							<button
								class="p-1 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 transition"
								aria-label="Download"
								on:click={() => item.type === 'image' ? downloadImage(item.id, item.name) : downloadDoc(item)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
								</svg>
							</button>
							<!-- Delete -->
							<button
								class="p-1 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-gray-400 hover:text-red-500 transition"
								aria-label="Delete"
								on:click={() => handleDelete(item.id)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
								</svg>
							</button>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>
{/if}
