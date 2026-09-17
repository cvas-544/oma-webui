<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        AddOmaUserModal.svelte
	// Description: OMA-specific Add User modal. Replaces the generic OWUI modal
	//              with a 3-tab (General / Permissions / Preview) form that
	//              captures RBAC role, Kürzel, plant/model/KB access, and admin
	//              toggle. No password — users authenticate via Azure AD SSO.
	// Author:      Vasu Chukka
	// ---------------------------------------------------------------------------
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	import { addUser } from '$lib/apis/auths';
	import { generateInitialsImage } from '$lib/utils';

	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import WrenchSolid from '$lib/components/icons/WrenchSolid.svelte';
	import UserPlusSolid from '$lib/components/icons/UserPlusSolid.svelte';

	import GeneralTab from './GeneralTab.svelte';
	import PermissionsTab from './PermissionsTab.svelte';
	import PreviewTab from './PreviewTab.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;

	// OMA static data passed in from UserList (fetched once there)
	export let allPlants: { plant_id: string; name: string }[] = [];
	export let allModels: { id: string; name: string }[] = [];
	export let allKnowledgeBases: { id: string; name: string }[] = [];

	// ── Form state ──────────────────────────────────────────────────────────────
	let selectedTab: 'general' | 'permissions' | 'preview' = 'general';
	let loading = false;

	let name = '';
	let email = '';
	let rbacRole = 'betriebsfuehrer';
	let kuerzel = '';
	let isAdmin = false;

	let selectedPlantIds: string[] = [];
	let selectedModelIds: string[] = [];
	let selectedKbIds: string[] = [];

	// Derived — full objects for preview
	$: selectedPlants = allPlants.filter((p) => selectedPlantIds.includes(p.plant_id));
	$: selectedModels = allModels.filter((m) => selectedModelIds.includes(m.id));
	$: selectedKbs = allKnowledgeBases.filter((kb) => selectedKbIds.includes(kb.id));

	const reset = () => {
		name = '';
		email = '';
		rbacRole = 'betriebsfuehrer';
		kuerzel = '';
		isAdmin = false;
		selectedPlantIds = [];
		selectedModelIds = [];
		selectedKbIds = [];
		selectedTab = 'general';
	};

	$: if (show) reset();

	const submitHandler = async () => {
		if (!name.trim() || !email.trim()) {
			toast.error('Name and email are required.');
			selectedTab = 'general';
			return;
		}

		loading = true;

		// OWUI account: role = 'admin' or 'user' (no password — SSO handles auth)
		// A random placeholder password is generated server-side; users never type it.
		const owuiRole = isAdmin ? 'admin' : 'user';
		const placeholderPassword = crypto.randomUUID();

		const res = await addUser(
			localStorage.token,
			name.trim(),
			email.trim().toLowerCase(),
			placeholderPassword,
			owuiRole,
			generateInitialsImage(name.trim())
		).catch((err) => {
			toast.error(`${err}`);
			return null;
		});

		if (res) {
			// TODO: after OWUI user is created, write OMA RBAC record:
			// POST /api/v1/oma/users  { email, rbac_role, kuerzel, plant_ids, models, kbs }
			// This will be wired once the OMA backend endpoint exists.
			// For now toast includes the OMA fields so they can be set manually.
			toast.success(
				`User "${name}" created. RBAC: ${rbacRole}, Plants: ${selectedPlantIds.length}, Models: ${selectedModelIds.length}.`
			);
			dispatch('save');
			show = false;
		}

		loading = false;
	};

	const TABS = [
		{ id: 'general', label: 'General' },
		{ id: 'permissions', label: 'Permissions' },
		{ id: 'preview', label: 'Preview' }
	] as const;
</script>

<Modal size="lg" bind:show>
	<div>
		<!-- Header -->
		<div class="flex justify-between dark:text-gray-100 px-4 pt-3 mb-1">
			<div class="text-sm font-medium self-center">{$i18n.t('Add User')}</div>
			<button
				class="self-center rounded-lg p-1 text-gray-500 transition hover:bg-gray-50 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
				on:click={() => { show = false; }}
				type="button"
				aria-label="Close"
			>
				<XMark className="size-4" />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full px-4 pb-4 md:space-x-4 dark:text-gray-200">
			<div class="flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={submitHandler}
				>
					<div class="flex flex-col lg:flex-row w-full h-full pb-2 lg:space-x-4">

						<!-- Left nav (mirrors EditGroupModal exactly) -->
						<div
							class="tabs flex flex-row overflow-x-auto gap-2.5 max-w-full lg:gap-1 lg:flex-col lg:flex-none lg:w-40 dark:text-gray-200 text-sm font-normal text-left scrollbar-none"
						>
							<!-- General -->
							<button
								class="px-0.5 py-1 max-w-fit w-fit rounded-lg flex-1 lg:flex-none flex text-right transition
									{selectedTab === 'general' ? '' : 'text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
								on:click={() => { selectedTab = 'general'; }}
								type="button"
							>
								<div class="self-center mr-2">
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
										<path fill-rule="evenodd" d="M6.955 1.45A.5.5 0 0 1 7.452 1h1.096a.5.5 0 0 1 .497.45l.17 1.699c.484.12.94.312 1.356.562l1.321-1.081a.5.5 0 0 1 .67.033l.774.775a.5.5 0 0 1 .034.67l-1.08 1.32c.25.417.44.873.561 1.357l1.699.17a.5.5 0 0 1 .45.497v1.096a.5.5 0 0 1-.45.497l-1.699.17c-.12.484-.312.94-.562 1.356l1.082 1.322a.5.5 0 0 1-.034.67l-.774.774a.5.5 0 0 1-.67.033l-1.322-1.08c-.416.25-.872.44-1.356.561l-.17 1.699a.5.5 0 0 1-.497.45H7.452a.5.5 0 0 1-.497-.45l-.17-1.699a4.973 4.973 0 0 1-1.356-.562L4.108 13.37a.5.5 0 0 1-.67-.033l-.774-.775a.5.5 0 0 1-.034-.67l1.08-1.32a4.971 4.971 0 0 1-.561-1.357l-1.699-.17A.5.5 0 0 1 1 8.548V7.452a.5.5 0 0 1 .45-.497l1.699-.17c.12-.484.312-.94.562-1.356L2.629 4.107a.5.5 0 0 1 .034-.67l.774-.774a.5.5 0 0 1 .67-.033L5.43 3.71a4.97 4.97 0 0 1 1.356-.561l.17-1.699ZM6 8c0 .538.212 1.026.558 1.385l.057.057a2 2 0 0 0 2.828-2.828l-.058-.056A2 2 0 0 0 6 8Z" clip-rule="evenodd" />
									</svg>
								</div>
								<div class="self-center">{$i18n.t('General')}</div>
							</button>

							<!-- Permissions -->
							<button
								class="px-0.5 py-1 max-w-fit w-fit rounded-lg flex-1 lg:flex-none flex text-right transition
									{selectedTab === 'permissions' ? '' : 'text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
								on:click={() => { selectedTab = 'permissions'; }}
								type="button"
							>
								<div class="self-center mr-2"><WrenchSolid /></div>
								<div class="self-center">{$i18n.t('Permissions')}</div>
							</button>

							<!-- Preview -->
							<button
								class="px-0.5 py-1 max-w-fit w-fit rounded-lg flex-1 lg:flex-none flex text-right transition
									{selectedTab === 'preview' ? '' : 'text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
								on:click={() => { selectedTab = 'preview'; }}
								type="button"
							>
								<div class="self-center mr-2">
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
										<path d="M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
										<path fill-rule="evenodd" d="M1.38 8.28a.87.87 0 0 1 0-.566 7.003 7.003 0 0 1 13.238.006.87.87 0 0 1 0 .566A7.003 7.003 0 0 1 1.379 8.28ZM11 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" clip-rule="evenodd" />
									</svg>
								</div>
								<div class="self-center">{$i18n.t('Preview')}</div>
							</button>
						</div>

						<!-- Right panel -->
						<div class="flex-1 mt-1 lg:mt-1 lg:h-[30rem] lg:max-h-[30rem] flex flex-col">
							<div class="w-full h-full overflow-y-auto scrollbar-hidden">
								{#if selectedTab === 'general'}
									<GeneralTab
										bind:name
										bind:email
										bind:rbacRole
										bind:kuerzel
										bind:isAdmin
									/>
								{:else if selectedTab === 'permissions'}
									<PermissionsTab
										{allPlants}
										{allModels}
										{allKnowledgeBases}
										bind:selectedPlantIds
										bind:selectedModelIds
										bind:selectedKbIds
									/>
								{:else if selectedTab === 'preview'}
									<PreviewTab
										{name}
										{email}
										{rbacRole}
										{kuerzel}
										{isAdmin}
										{selectedPlants}
										{selectedModels}
										{selectedKbs}
									/>
								{/if}
							</div>

							<!-- Save footer (always visible) -->
							<div class="flex justify-end pt-3 text-sm font-normal">
								<button
									class="px-3.5 py-1.5 text-sm font-normal bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full flex items-center gap-2 whitespace-nowrap
										{loading ? 'cursor-not-allowed opacity-70' : ''}"
									type="submit"
									disabled={loading}
								>
									{$i18n.t('Save')}
									{#if loading}
										<span class="shrink-0"><Spinner /></span>
									{/if}
								</button>
							</div>
						</div>

					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>
