<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        QuickSettingsMenu.svelte
	// Description: Fluid circular quick-settings menu for the Navbar top-right.
	//              Trigger (gear→X) expands downward: Feedback, Theme, Logout, Settings.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------
	import { theme, user } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { userSignOut } from '$lib/apis/auths';
	import Bars3BottomLeft from '$lib/components/icons/Bars3BottomLeft.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import ChatBubble from '$lib/components/icons/ChatBubble.svelte';
	import SignOut from '$lib/components/icons/SignOut.svelte';
	import Cog6 from '$lib/components/icons/Cog6.svelte';

	let expanded = false;

	// ── Theme ─────────────────────────────────────────────────────────────────
	function applyTheme(_theme: string) {
		const toApply =
			_theme === 'system'
				? window.matchMedia('(prefers-color-scheme: dark)').matches
					? 'dark'
					: 'light'
				: _theme;
		['light', 'dark'].filter((c) => c !== toApply).forEach((c) => document.documentElement.classList.remove(c));
		document.documentElement.classList.add(toApply);
		document.querySelector('meta[name="theme-color"]')?.setAttribute('content', toApply === 'dark' ? '#171717' : '#ffffff');
		if (typeof window !== 'undefined' && (window as any).applyTheme) (window as any).applyTheme();
	}

	$: isDark = ($theme ?? (typeof localStorage !== 'undefined' ? localStorage.theme : 'light')) === 'dark';

	function toggleTheme() {
		const next = isDark ? 'light' : 'dark';
		theme.set(next);
		localStorage.setItem('theme', next);
		applyTheme(next);
		expanded = false;
	}

	// ── Logout ────────────────────────────────────────────────────────────────
	async function handleLogout() {
		expanded = false;
		const res = await userSignOut().catch(() => null);
		user.set(null);
		localStorage.removeItem('token');
		location.href = (res as any)?.redirect_url ?? '/auth';
	}

	// ── Navigation ────────────────────────────────────────────────────────────
	function handleSettings() {
		expanded = false;
		goto('/settings');
	}

	// ── Feedback (Phase 6) ────────────────────────────────────────────────────
	function handleFeedback() {
		expanded = false;
		// TODO: open free-feedback modal (Phase 6)
	}
</script>

<!-- Click-outside backdrop -->
{#if expanded}
	<div class="fixed inset-0 z-[39]" on:click={() => (expanded = false)} aria-hidden="true"></div>
{/if}

<!-- Menu root — fixed 36px wide so items stack cleanly -->
<div class="relative" style="width:36px;">

	<!-- ── Trigger ──────────────────────────────────────────────────────────── -->
	<button
		class="relative w-9 h-9 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors cursor-pointer z-50 will-change-transform"
		on:click={() => (expanded = !expanded)}
		aria-label={expanded ? 'Close menu' : 'Quick settings'}
		aria-expanded={expanded}
	>
		<!-- Menu (hamburger) — visible when collapsed -->
		<span
			class="absolute inset-0 flex items-center justify-center transition-all duration-300 origin-center"
			style="opacity:{expanded ? 0 : 1}; transform:scale({expanded ? 0 : 1}) rotate({expanded ? 90 : 0}deg);"
		>
			<Bars3BottomLeft className="size-4" />
		</span>

		<!-- X — visible when expanded -->
		<span
			class="absolute inset-0 flex items-center justify-center transition-all duration-300 origin-center"
			style="opacity:{expanded ? 1 : 0}; transform:scale({expanded ? 1 : 0}) rotate({expanded ? 0 : -90}deg);"
		>
			<XMark className="size-4" />
		</span>
	</button>

	<!-- ── Item 1: Feedback ─────────────────────────────────────────────────── -->
	<div
		class="absolute top-0 left-0 w-9 h-9 bg-gray-100 dark:bg-gray-800 will-change-transform"
		style="
			transform: translateY({expanded ? 40 : 0}px);
			opacity: {expanded ? 1 : 0};
			z-index: 48;
			clip-path: circle(50% at 50% 55%);
			transition: transform 300ms cubic-bezier(0.4,0,0.2,1), opacity {expanded ? 260 : 320}ms;
			pointer-events: {expanded ? 'auto' : 'none'};
		"
	>
		<button
			class="w-full h-full flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-[#003877] dark:hover:text-[#73B2F2] transition-colors"
			on:click={handleFeedback}
			aria-label="Send feedback"
		>
			<ChatBubble className="size-4" strokeWidth="1.75" />
		</button>
	</div>

	<!-- ── Item 2: Theme toggle ─────────────────────────────────────────────── -->
	<div
		class="absolute top-0 left-0 w-9 h-9 bg-gray-100 dark:bg-gray-800 will-change-transform"
		style="
			transform: translateY({expanded ? 80 : 0}px);
			opacity: {expanded ? 1 : 0};
			z-index: 47;
			clip-path: circle(50% at 50% 55%);
			transition: transform 300ms cubic-bezier(0.4,0,0.2,1), opacity {expanded ? 280 : 300}ms;
			pointer-events: {expanded ? 'auto' : 'none'};
		"
	>
		<button
			class="w-full h-full flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-[#003877] dark:hover:text-[#73B2F2] transition-colors"
			on:click={toggleTheme}
			aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
		>
			{#if isDark}
				<!-- Sun icon — shown in dark mode (click → go light) -->
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="4"/>
					<line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/>
					<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
					<line x1="2" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22" y2="12"/>
					<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
				</svg>
			{:else}
				<!-- Moon icon — shown in light mode (click → go dark) -->
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
				</svg>
			{/if}
		</button>
	</div>

	<!-- ── Item 3: Logout ───────────────────────────────────────────────────── -->
	<div
		class="absolute top-0 left-0 w-9 h-9 bg-gray-100 dark:bg-gray-800 will-change-transform"
		style="
			transform: translateY({expanded ? 120 : 0}px);
			opacity: {expanded ? 1 : 0};
			z-index: 46;
			clip-path: circle(50% at 50% 55%);
			transition: transform 300ms cubic-bezier(0.4,0,0.2,1), opacity {expanded ? 300 : 280}ms;
			pointer-events: {expanded ? 'auto' : 'none'};
		"
	>
		<button
			class="w-full h-full flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
			on:click={handleLogout}
			aria-label="Sign out"
		>
			<SignOut className="size-4" strokeWidth="1.75" />
		</button>
	</div>

	<!-- ── Item 4: Settings ─────────────────────────────────────────────────── -->
	<div
		class="absolute top-0 left-0 w-9 h-9 bg-gray-100 dark:bg-gray-800 will-change-transform"
		style="
			transform: translateY({expanded ? 160 : 0}px);
			opacity: {expanded ? 1 : 0};
			z-index: 45;
			clip-path: circle(50% at 50% 50%);
			transition: transform 300ms cubic-bezier(0.4,0,0.2,1), opacity {expanded ? 320 : 260}ms;
			pointer-events: {expanded ? 'auto' : 'none'};
		"
	>
		<button
			class="w-full h-full flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-[#003877] dark:hover:text-[#73B2F2] transition-colors"
			on:click={handleSettings}
			aria-label="Settings"
		>
			<Cog6 className="size-4" strokeWidth="1.75" />
		</button>
	</div>

</div>
