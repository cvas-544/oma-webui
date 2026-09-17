<script lang="ts">
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	export let name = '';
	export let email = '';
	export let rbacRole = 'betriebsfuehrer';
	export let kuerzel = '';
	export let isAdmin = false;
	export let onDelete: Function = () => {};
	export let edit = false;

	const RBAC_ROLES = [
		{ value: 'betriebsfuehrer', label: 'Betriebsführer' },
		{ value: 'developer', label: 'Developer' },
		{ value: 'teamleiter', label: 'Teamleiter' },
		{ value: 'reporting', label: 'Reporting' },
		{ value: 'leadership', label: 'Leadership' }
	];
</script>

<div class="flex flex-col gap-4 pr-1">
	<!-- Name -->
	<div class="flex flex-col w-full">
		<div class="mb-1 text-xs text-gray-500">{$i18n.t('Name')}</div>
		<input
			class="w-full text-sm bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden"
			type="text"
			bind:value={name}
			placeholder={$i18n.t('Full Name')}
			autocomplete="off"
			required
		/>
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Email -->
	<div class="flex flex-col w-full">
		<div class="mb-1 flex items-center gap-1">
			<span class="text-xs text-gray-500">{$i18n.t('Email')}</span>
			<div class="relative group/tip">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 text-gray-400 cursor-help">
					<path fill-rule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0ZM9 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6.75 8a.75.75 0 0 0 0 1.5h.75v1.75a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8.25 8h-1.5Z" clip-rule="evenodd" />
				</svg>
				<div class="absolute left-0 bottom-full mb-2 w-56 px-2.5 py-2 text-xs text-gray-100 bg-gray-800 dark:bg-gray-700 rounded-lg shadow-lg opacity-0 group-hover/tip:opacity-100 pointer-events-none transition-opacity duration-150 z-50 whitespace-normal leading-relaxed">
					{$i18n.t('Must match their Microsoft account email. Used for Azure AD SSO login.')}
					<div class="absolute left-3 top-full w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-gray-800 dark:border-t-gray-700"></div>
				</div>
			</div>
		</div>
		<input
			class="w-full text-sm bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden"
			type="email"
			bind:value={email}
			placeholder="user@enerparc.com"
			autocomplete="off"
			required
		/>
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- RBAC Role -->
	<div class="flex flex-col w-full">
		<div class="mb-1 flex items-center gap-1">
			<span class="text-xs text-gray-500">{$i18n.t('RBAC Role')}</span>
			<div class="relative group/tip">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 text-gray-400 cursor-help">
					<path fill-rule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0ZM9 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6.75 8a.75.75 0 0 0 0 1.5h.75v1.75a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8.25 8h-1.5Z" clip-rule="evenodd" />
				</svg>
				<div class="absolute left-0 bottom-full mb-2 w-56 px-2.5 py-2 text-xs text-gray-100 bg-gray-800 dark:bg-gray-700 rounded-lg shadow-lg opacity-0 group-hover/tip:opacity-100 pointer-events-none transition-opacity duration-150 z-50 whitespace-normal leading-relaxed">
					{$i18n.t('Controls which solar plant data this user can see.')}
					<div class="absolute left-3 top-full w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-gray-800 dark:border-t-gray-700"></div>
				</div>
			</div>
		</div>
		<select
			class="w-full text-sm bg-transparent outline-hidden rounded-lg capitalize"
			bind:value={rbacRole}
			required
		>
			{#each RBAC_ROLES as r}
				<option value={r.value}>{r.label}</option>
			{/each}
		</select>
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Kuerzel -->
	<div class="flex flex-col w-full">
		<div class="mb-1 flex items-center gap-1">
			<span class="text-xs text-gray-500">{$i18n.t('Kürzel')}</span>
			<div class="relative group/tip">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 text-gray-400 cursor-help">
					<path fill-rule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0ZM9 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6.75 8a.75.75 0 0 0 0 1.5h.75v1.75a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8.25 8h-1.5Z" clip-rule="evenodd" />
				</svg>
				<div class="absolute left-0 bottom-full mb-2 w-56 px-2.5 py-2 text-xs text-gray-100 bg-gray-800 dark:bg-gray-700 rounded-lg shadow-lg opacity-0 group-hover/tip:opacity-100 pointer-events-none transition-opacity duration-150 z-50 whitespace-normal leading-relaxed">
					{$i18n.t('Short identifier used for validation in the CLI (2–5 uppercase letters).')}
					<div class="absolute left-3 top-full w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-gray-800 dark:border-t-gray-700"></div>
				</div>
			</div>
		</div>
		<input
			class="w-full text-sm bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden uppercase"
			type="text"
			bind:value={kuerzel}
			placeholder={$i18n.t('e.g. MGL, BEC')}
			autocomplete="off"
			maxlength="5"
			on:input={(e) => { kuerzel = e.currentTarget.value.toUpperCase(); }}
		/>
	</div>

	<hr class="border-gray-100 dark:border-gray-850/30" />

	<!-- Admin toggle -->
	<div class="flex w-full justify-between items-center">
		<div class="flex items-center gap-1">
			<div class="text-sm">{$i18n.t('Admin access')}</div>
			<div class="relative group/tip">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 text-gray-400 cursor-help">
					<path fill-rule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0ZM9 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6.75 8a.75.75 0 0 0 0 1.5h.75v1.75a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8.25 8h-1.5Z" clip-rule="evenodd" />
				</svg>
				<div class="absolute left-0 bottom-full mb-2 w-56 px-2.5 py-2 text-xs text-gray-100 bg-gray-800 dark:bg-gray-700 rounded-lg shadow-lg opacity-0 group-hover/tip:opacity-100 pointer-events-none transition-opacity duration-150 z-50 whitespace-normal leading-relaxed">
					{$i18n.t('Grants full UI admin panel access. Only for internal developers.')}
					<div class="absolute left-3 top-full w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-gray-800 dark:border-t-gray-700"></div>
				</div>
			</div>
		</div>
		<button
			type="button"
			class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none {isAdmin
				? 'bg-black dark:bg-white'
				: 'bg-gray-200 dark:bg-gray-700'}"
			role="switch"
			aria-checked={isAdmin}
			aria-label="Toggle admin access"
			on:click={() => { isAdmin = !isAdmin; }}
		>
			<span
				class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white dark:bg-black shadow ring-0 transition duration-200 ease-in-out {isAdmin
					? 'translate-x-4'
					: 'translate-x-0'}"
			></span>
		</button>
	</div>

	{#if edit}
		<hr class="border-gray-100 dark:border-gray-850/30" />

		<!-- Actions -->
		<div class="flex flex-col w-full">
			<div class="mb-1 text-xs text-gray-500">{$i18n.t('Actions')}</div>
			<button
				class="text-xs text-red-500 hover:underline cursor-pointer text-left"
				type="button"
				on:click={() => onDelete()}
			>
				{$i18n.t('Delete')} {$i18n.t('user access')}
			</button>
		</div>
	{/if}
</div>
