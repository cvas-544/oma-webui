<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        ThemeSwitcher.svelte
	// Description: Light / Dark / System theme pill for the Navbar top-right.
	//              Icon-only tabs, no labels. Mirrors the applyTheme logic from
	//              Settings/General.svelte so both stay in sync.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------
	import { theme } from '$lib/stores';

	const THEMES = ['light', 'dark', 'system'] as const;
	type ThemeVal = (typeof THEMES)[number];

	function applyTheme(_theme: string) {
		const allClasses = ['light', 'dark'];
		let themeToApply = _theme;
		if (_theme === 'system') {
			themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
		}
		allClasses
			.filter((c) => c !== themeToApply)
			.forEach((c) => document.documentElement.classList.remove(c));
		document.documentElement.classList.add(themeToApply);

		const meta = document.querySelector('meta[name="theme-color"]');
		if (meta) {
			meta.setAttribute('content', themeToApply === 'dark' ? '#171717' : '#ffffff');
		}
		if (typeof window !== 'undefined' && (window as any).applyTheme) {
			(window as any).applyTheme();
		}
	}

	function setTheme(val: ThemeVal) {
		theme.set(val);
		localStorage.setItem('theme', val);
		applyTheme(val);
	}

	$: current = ($theme as ThemeVal) ?? (localStorage?.theme as ThemeVal) ?? 'system';
</script>

<div class="flex items-center rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-850 p-0.5 gap-0.5">
	<!-- Light -->
	<button
		title="Light"
		on:click={() => setTheme('light')}
		class="flex items-center justify-center w-7 h-7 rounded-lg transition-all
			{current === 'light'
				? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white'
				: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}"
	>
		<!-- Sun icon -->
		<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
			<circle cx="12" cy="12" r="4"/>
			<line x1="12" y1="2" x2="12" y2="4"/>
			<line x1="12" y1="20" x2="12" y2="22"/>
			<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
			<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
			<line x1="2" y1="12" x2="4" y2="12"/>
			<line x1="20" y1="12" x2="22" y2="12"/>
			<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
			<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
		</svg>
	</button>

	<!-- Dark -->
	<button
		title="Dark"
		on:click={() => setTheme('dark')}
		class="flex items-center justify-center w-7 h-7 rounded-lg transition-all
			{current === 'dark'
				? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white'
				: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}"
	>
		<!-- Moon icon -->
		<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
			<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
		</svg>
	</button>

	<!-- System -->
	<button
		title="System"
		on:click={() => setTheme('system')}
		class="flex items-center justify-center w-7 h-7 rounded-lg transition-all
			{current === 'system'
				? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white'
				: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}"
	>
		<!-- Monitor icon -->
		<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
			<rect x="2" y="3" width="20" height="14" rx="2"/>
			<line x1="8" y1="21" x2="16" y2="21"/>
			<line x1="12" y1="17" x2="12" y2="21"/>
		</svg>
	</button>
</div>
