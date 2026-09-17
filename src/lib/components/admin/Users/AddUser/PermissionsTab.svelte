<script lang="ts">
	import { getContext } from 'svelte';
	import Search from '$lib/components/icons/Search.svelte';
	const i18n = getContext('i18n');

	export let allPlants: { plant_id: string; name: string }[] = [];
	export let allModels: { id: string; name: string }[] = [];
	export let allKnowledgeBases: { id: string; name: string }[] = [];

	export let selectedPlantIds: string[] = [];
	export let selectedModelIds: string[] = [];
	export let selectedKbIds: string[] = [];

	type PermTab = 'plants' | 'models' | 'knowledge';
	let activePermTab: PermTab = 'plants';
	let plantSearch = '';
	let modelSearch = '';
	let kbSearch = '';

	$: filteredPlants = allPlants.filter((p) => {
		const q = plantSearch.trim();
		if (!q) return true;
		return (
			p.name.toLowerCase().includes(q.toLowerCase()) ||
			p.plant_id.includes(q)
		);
	});

	$: filteredModels = allModels.filter((m) => {
		const q = modelSearch.trim();
		if (!q) return true;
		return m.name.toLowerCase().includes(q.toLowerCase()) || m.id.toLowerCase().includes(q.toLowerCase());
	});

	$: filteredKbs = allKnowledgeBases.filter((kb) => {
		const q = kbSearch.trim();
		if (!q) return true;
		return kb.name.toLowerCase().includes(q.toLowerCase());
	});

	function togglePlant(id: string) {
		if (selectedPlantIds.includes(id)) {
			selectedPlantIds = selectedPlantIds.filter((p) => p !== id);
		} else {
			selectedPlantIds = [...selectedPlantIds, id];
		}
	}

	function toggleModel(id: string) {
		if (selectedModelIds.includes(id)) {
			selectedModelIds = selectedModelIds.filter((m) => m !== id);
		} else {
			selectedModelIds = [...selectedModelIds, id];
		}
	}

	function toggleKb(id: string) {
		if (selectedKbIds.includes(id)) {
			selectedKbIds = selectedKbIds.filter((k) => k !== id);
		} else {
			selectedKbIds = [...selectedKbIds, id];
		}
	}

	function selectAllPlants() {
		selectedPlantIds = filteredPlants.map((p) => p.plant_id);
	}
	function clearAllPlants() {
		const filteredIds = new Set(filteredPlants.map((p) => p.plant_id));
		selectedPlantIds = selectedPlantIds.filter((id) => !filteredIds.has(id));
	}
</script>

<div class="flex flex-col h-full gap-3">
	<!-- Filter pills -->
	<div class="flex gap-1.5 flex-wrap">
		<button
			type="button"
			class="px-3 py-1 text-xs rounded-full transition font-medium
				{activePermTab === 'plants'
					? 'bg-black text-white dark:bg-white dark:text-black'
					: 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}"
			on:click={() => { activePermTab = 'plants'; }}
		>
			{$i18n.t('Plants')}
			{#if selectedPlantIds.length > 0}
				<span class="ml-1 opacity-60">({selectedPlantIds.length})</span>
			{/if}
		</button>

		<button
			type="button"
			class="px-3 py-1 text-xs rounded-full transition font-medium
				{activePermTab === 'models'
					? 'bg-black text-white dark:bg-white dark:text-black'
					: 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}"
			on:click={() => { activePermTab = 'models'; }}
		>
			{$i18n.t('Models')}
			{#if selectedModelIds.length > 0}
				<span class="ml-1 opacity-60">({selectedModelIds.length})</span>
			{/if}
		</button>

		<button
			type="button"
			class="px-3 py-1 text-xs rounded-full transition font-medium
				{activePermTab === 'knowledge'
					? 'bg-black text-white dark:bg-white dark:text-black'
					: 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}"
			on:click={() => { activePermTab = 'knowledge'; }}
		>
			{$i18n.t('Knowledge Bases')}
			{#if selectedKbIds.length > 0}
				<span class="ml-1 opacity-60">({selectedKbIds.length})</span>
			{/if}
		</button>
	</div>

	<!-- Plants panel -->
	{#if activePermTab === 'plants'}
		<div class="flex flex-col gap-2 flex-1 min-h-0">
			<div class="flex items-center gap-2">
				<div class="flex flex-1 items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-2.5 py-1.5">
					<Search className="size-3.5 text-gray-400 flex-shrink-0" />
					<input
						class="flex-1 text-xs bg-transparent outline-hidden placeholder:text-gray-400"
						bind:value={plantSearch}
						placeholder={$i18n.t('Search by name or plant ID…')}
					/>
				</div>
				<button
					type="button"
					class="text-xs text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 whitespace-nowrap"
					on:click={selectAllPlants}
				>{$i18n.t('All')}</button>
				<span class="text-gray-300 dark:text-gray-700 text-xs">·</span>
				<button
					type="button"
					class="text-xs text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 whitespace-nowrap"
					on:click={clearAllPlants}
				>{$i18n.t('None')}</button>
			</div>

			<div class="flex-1 overflow-y-auto scrollbar-hidden flex flex-col gap-0.5">
				{#if filteredPlants.length === 0}
					<div class="text-xs text-gray-400 text-center py-6">{$i18n.t('No plants found.')}</div>
				{:else}
					{#each filteredPlants as plant (plant.plant_id)}
						<button
							type="button"
							class="flex items-center justify-between w-full px-2 py-1.5 rounded-lg text-left transition
								{selectedPlantIds.includes(plant.plant_id)
									? 'bg-gray-100 dark:bg-gray-800'
									: 'hover:bg-gray-50 dark:hover:bg-gray-900'}"
							on:click={() => togglePlant(plant.plant_id)}
						>
							<div class="flex items-center gap-2 min-w-0">
								<div
									class="flex-shrink-0 w-3.5 h-3.5 rounded border transition
										{selectedPlantIds.includes(plant.plant_id)
											? 'bg-black dark:bg-white border-black dark:border-white'
											: 'border-gray-300 dark:border-gray-600'}"
								>
									{#if selectedPlantIds.includes(plant.plant_id)}
										<svg viewBox="0 0 10 10" class="w-full h-full text-white dark:text-black p-0.5">
											<polyline points="1.5,5 4,7.5 8.5,2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
										</svg>
									{/if}
								</div>
								<span class="text-xs text-gray-900 dark:text-white truncate">{plant.name}</span>
							</div>
							<span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-2 font-mono">
								{plant.plant_id}
							</span>
						</button>
					{/each}
				{/if}
			</div>

			<div class="text-xs text-gray-400 pt-1">
				{selectedPlantIds.length} {$i18n.t('of')} {allPlants.length} {$i18n.t('plants selected')}
			</div>
		</div>
	{/if}

	<!-- Models panel -->
	{#if activePermTab === 'models'}
		<div class="flex flex-col gap-2 flex-1 min-h-0">
			<div class="flex items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-2.5 py-1.5">
				<Search className="size-3.5 text-gray-400 flex-shrink-0" />
				<input
					class="flex-1 text-xs bg-transparent outline-hidden placeholder:text-gray-400"
					bind:value={modelSearch}
					placeholder={$i18n.t('Search models…')}
				/>
			</div>

			<div class="flex-1 overflow-y-auto scrollbar-hidden flex flex-col gap-0.5">
				{#if filteredModels.length === 0}
					<div class="text-xs text-gray-400 text-center py-6">{$i18n.t('No models found.')}</div>
				{:else}
					{#each filteredModels as model (model.id)}
						<button
							type="button"
							class="flex items-center gap-2 w-full px-2 py-1.5 rounded-lg text-left transition
								{selectedModelIds.includes(model.id)
									? 'bg-gray-100 dark:bg-gray-800'
									: 'hover:bg-gray-50 dark:hover:bg-gray-900'}"
							on:click={() => toggleModel(model.id)}
						>
							<div
								class="flex-shrink-0 w-3.5 h-3.5 rounded border transition
									{selectedModelIds.includes(model.id)
										? 'bg-black dark:bg-white border-black dark:border-white'
										: 'border-gray-300 dark:border-gray-600'}"
							>
								{#if selectedModelIds.includes(model.id)}
									<svg viewBox="0 0 10 10" class="w-full h-full text-white dark:text-black p-0.5">
										<polyline points="1.5,5 4,7.5 8.5,2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									</svg>
								{/if}
							</div>
							<div class="min-w-0">
								<div class="text-xs text-gray-900 dark:text-white truncate">{model.name}</div>
								<div class="text-xs text-gray-400 font-mono truncate">{model.id}</div>
							</div>
						</button>
					{/each}
				{/if}
			</div>

			<div class="text-xs text-gray-400 pt-1">
				{selectedModelIds.length} {$i18n.t('of')} {allModels.length} {$i18n.t('models selected')}
			</div>
		</div>
	{/if}

	<!-- Knowledge bases panel -->
	{#if activePermTab === 'knowledge'}
		<div class="flex flex-col gap-2 flex-1 min-h-0">
			<div class="flex items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-2.5 py-1.5">
				<Search className="size-3.5 text-gray-400 flex-shrink-0" />
				<input
					class="flex-1 text-xs bg-transparent outline-hidden placeholder:text-gray-400"
					bind:value={kbSearch}
					placeholder={$i18n.t('Search knowledge bases…')}
				/>
			</div>

			<div class="flex-1 overflow-y-auto scrollbar-hidden flex flex-col gap-0.5">
				{#if filteredKbs.length === 0}
					<div class="text-xs text-gray-400 text-center py-6">{$i18n.t('No knowledge bases found.')}</div>
				{:else}
					{#each filteredKbs as kb (kb.id)}
						<button
							type="button"
							class="flex items-center gap-2 w-full px-2 py-1.5 rounded-lg text-left transition
								{selectedKbIds.includes(kb.id)
									? 'bg-gray-100 dark:bg-gray-800'
									: 'hover:bg-gray-50 dark:hover:bg-gray-900'}"
							on:click={() => toggleKb(kb.id)}
						>
							<div
								class="flex-shrink-0 w-3.5 h-3.5 rounded border transition
									{selectedKbIds.includes(kb.id)
										? 'bg-black dark:bg-white border-black dark:border-white'
										: 'border-gray-300 dark:border-gray-600'}"
							>
								{#if selectedKbIds.includes(kb.id)}
									<svg viewBox="0 0 10 10" class="w-full h-full text-white dark:text-black p-0.5">
										<polyline points="1.5,5 4,7.5 8.5,2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									</svg>
								{/if}
							</div>
							<span class="text-xs text-gray-900 dark:text-white truncate">{kb.name}</span>
						</button>
					{/each}
				{/if}
			</div>

			<div class="text-xs text-gray-400 pt-1">
				{selectedKbIds.length} {$i18n.t('of')} {allKnowledgeBases.length} {$i18n.t('knowledge bases selected')}
			</div>
		</div>
	{/if}
</div>
