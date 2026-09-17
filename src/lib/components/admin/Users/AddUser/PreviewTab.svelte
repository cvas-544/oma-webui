<script lang="ts">
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	export let name = '';
	export let email = '';
	export let rbacRole = '';
	export let kuerzel = '';
	export let isAdmin = false;
	export let selectedPlants: { plant_id: string; name: string }[] = [];
	export let selectedModels: { id: string; name: string }[] = [];
	export let selectedKbs: { id: string; name: string }[] = [];

	const RBAC_LABEL: Record<string, string> = {
		betriebsfuehrer: 'Betriebsführer',
		developer: 'Developer',
		teamleiter: 'Teamleiter',
		reporting: 'Reporting',
		leadership: 'Leadership'
	};
</script>

<div class="flex flex-col gap-4 overflow-y-auto scrollbar-hidden pr-1">
	<!-- Identity -->
	<div>
		<div class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-medium">{$i18n.t('Identity')}</div>
		<div class="flex flex-col gap-2">
			<div class="flex justify-between text-xs">
				<span class="text-gray-500">{$i18n.t('Name')}</span>
				<span class="text-gray-900 dark:text-white font-medium">{name || '-'}</span>
			</div>
			<div class="flex justify-between text-xs">
				<span class="text-gray-500">{$i18n.t('Email')}</span>
				<span class="text-gray-900 dark:text-white font-mono">{email || '-'}</span>
			</div>
			<div class="flex justify-between text-xs">
				<span class="text-gray-500">{$i18n.t('RBAC Role')}</span>
				<span class="text-gray-900 dark:text-white">{(RBAC_LABEL[rbacRole] ?? rbacRole) || '-'}</span>
			</div>
			<div class="flex justify-between text-xs">
				<span class="text-gray-500">{$i18n.t('Kürzel')}</span>
				<span class="text-gray-900 dark:text-white font-mono">{kuerzel || '-'}</span>
			</div>
			<div class="flex justify-between text-xs">
				<span class="text-gray-500">{$i18n.t('UI Admin')}</span>
				<span class="{isAdmin ? 'text-amber-500' : 'text-gray-400'}">
					{isAdmin ? $i18n.t('Yes') : $i18n.t('No')}
				</span>
			</div>
		</div>
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Plants -->
	<div>
		<div class="flex justify-between items-center mb-2">
			<div class="text-xs text-gray-500 uppercase tracking-wide font-medium">{$i18n.t('Plants')}</div>
			<span class="text-xs text-gray-400">{selectedPlants.length} {$i18n.t('assigned')}</span>
		</div>

		{#if selectedPlants.length === 0}
			<div class="text-xs text-gray-400 italic">{$i18n.t('No plants assigned. User will see no plant data.')}</div>
		{:else}
			<div class="flex flex-col gap-1">
				{#each selectedPlants as plant (plant.plant_id)}
					<div class="flex justify-between text-xs">
						<span class="text-gray-900 dark:text-white">{plant.name}</span>
						<span class="text-gray-400 font-mono">{plant.plant_id}</span>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Models -->
	<div>
		<div class="flex justify-between items-center mb-2">
			<div class="text-xs text-gray-500 uppercase tracking-wide font-medium">{$i18n.t('Models')}</div>
			<span class="text-xs text-gray-400">{selectedModels.length} {$i18n.t('assigned')}</span>
		</div>

		{#if selectedModels.length === 0}
			<div class="text-xs text-gray-400 italic">{$i18n.t('No models assigned.')}</div>
		{:else}
			<div class="flex flex-col gap-1">
				{#each selectedModels as model (model.id)}
					<div class="flex justify-between text-xs">
						<span class="text-gray-900 dark:text-white">{model.name}</span>
						<span class="text-gray-400 font-mono">{model.id}</span>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Knowledge Bases -->
	<div>
		<div class="flex justify-between items-center mb-2">
			<div class="text-xs text-gray-500 uppercase tracking-wide font-medium">{$i18n.t('Knowledge Bases')}</div>
			<span class="text-xs text-gray-400">{selectedKbs.length} {$i18n.t('assigned')}</span>
		</div>

		{#if selectedKbs.length === 0}
			<div class="text-xs text-gray-400 italic">{$i18n.t('No knowledge bases assigned.')}</div>
		{:else}
			<div class="flex flex-col gap-1">
				{#each selectedKbs as kb (kb.id)}
					<div class="text-xs text-gray-900 dark:text-white">{kb.name}</div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Validation warning -->
	{#if !name || !email}
		<div class="mt-2 px-3 py-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-xs text-amber-700 dark:text-amber-400">
			{$i18n.t('Name and email are required before saving.')}
		</div>
	{/if}
</div>
