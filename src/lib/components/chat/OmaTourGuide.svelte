<!-- ---------------------------------------------------------------------------
  File:        OmaTourGuide.svelte
  Description: OMA quick tour guide — step-by-step overlay that highlights
               key UI elements with a tooltip card and Enerparc glow effect.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { showOmaTour } from '$lib/stores/omaTour';
	import XMark from '$lib/components/icons/XMark.svelte';
	import ArrowLeft from '$lib/components/icons/ArrowLeft.svelte';
	import ArrowRight from '$lib/components/icons/ArrowRight.svelte';

	// ── Step definitions ────────────────────────────────────────────────────────

	type TourStep = {
		target: string | null;
		title: string;
		description: string;
		position: 'top' | 'bottom' | 'left' | 'right' | 'center';
	};

	const STEPS: TourStep[] = [
		{
			target: null,
			title: 'Welcome to OMA Agent',
			description: 'Your AI-powered assistant for solar plant operations & maintenance. This quick tour shows you the key features — takes less than a minute.',
			position: 'center'
		},
		{
			target: '[data-tour="chat-input"]',
			title: 'Chat with your plant',
			description: 'Ask anything in plain language — performance issues, fault analysis, maintenance schedules, document lookups. The agent knows your plant data.',
			position: 'top'
		},
		{
			target: '[data-tour="suggestions"]',
			title: 'Quick-start prompts',
			description: 'Not sure where to start? Pick one of these O&M-specific prompts. They\'re tailored to the most common plant questions.',
			position: 'top'
		},
		{
			target: '[data-tour="prompt-library"]',
			title: 'Prompt Library',
			description: 'Browse curated prompts for performance analysis, fault diagnosis, reporting, and more. Click one to pre-fill your message.',
			position: 'top'
		},
		{
			target: '[data-tour="knowledge-base"]',
			title: 'Knowledge Base',
			description: 'Access all plant documents organized by category and priority — contracts, plans, commissioning reports, O&M manuals and more.',
			position: 'top'
		},
		{
			target: '[data-tour="sidebar-folders"]',
			title: 'Folders',
			description: 'Organize your conversations into folders — group related chats by plant, project, or task to keep your workspace tidy.',
			position: 'right'
		},
		{
			target: '[data-tour="sidebar-artifacts"]',
			title: 'Artifacts',
			description: 'Charts, tables, and files generated during your chats appear here. Quickly revisit or export any artifact from a previous session.',
			position: 'right'
		},
		{
			target: '[data-tour="quick-settings"]',
			title: 'Quick Settings',
			description: 'Access model parameters, display preferences, and chat controls instantly — without leaving your conversation.',
			position: 'left'
		},
		{
			target: '[data-tour="sidebar-profile"]',
			title: 'Profile & Settings',
			description: 'Manage your account, preferences, and OMA profile. Switch themes or access admin settings from here.',
			position: 'top'
		},
		{
			target: '[data-tour="feedback"]',
			title: 'Give Feedback',
			description: 'Found something useful — or something off? Your feedback helps us improve OMA for the whole team.',
			position: 'top'
		}
	];

	// ── State ───────────────────────────────────────────────────────────────────

	let currentStep = 0;
	let targetRect: DOMRect | null = null;
	let windowW = 0;
	let windowH = 0;

	// DOM elevation — lifts the target element above the gradient layer
	let activeEl: HTMLElement | null = null;
	let savedPosition = '';
	let savedZIndex = '';

	const TOOLTIP_W = 300;
	const PAD = 16;

	// ── Reactive helpers ────────────────────────────────────────────────────────

	$: step = STEPS[currentStep];
	$: isFirst = currentStep === 0;
	$: isLast = currentStep === STEPS.length - 1;

	function restoreEl() {
		if (activeEl) {
			activeEl.style.position = savedPosition;
			activeEl.style.zIndex = savedZIndex;
			activeEl = null;
		}
	}

	async function updateRect() {
		await tick();
		windowW = window.innerWidth;
		windowH = window.innerHeight;

		restoreEl();

		if (!step?.target) { targetRect = null; return; }
		const el = document.querySelector(step.target) as HTMLElement | null;
		targetRect = el ? el.getBoundingClientRect() : null;

		// Elevate target above gradient (99991) so gradient sits behind it
		if (el) {
			activeEl = el;
			savedPosition = el.style.position;
			savedZIndex   = el.style.zIndex;
			el.style.position = 'relative';
			el.style.zIndex   = '99993';
		}
	}

	$: if ($showOmaTour) updateRect();
	$: currentStep, $showOmaTour && updateRect();

	// ── Navigation ──────────────────────────────────────────────────────────────

	function next() {
		if (!isLast) currentStep++;
		else close();
	}

	function prev() {
		if (!isFirst) currentStep--;
	}

	function close() {
		restoreEl();
		showOmaTour.set(false);
		currentStep = 0;
	}

	function handleKey(e: KeyboardEvent) {
		if (!$showOmaTour) return;
		if (e.key === 'Escape')      close();
		if (e.key === 'ArrowRight')  next();
		if (e.key === 'ArrowLeft')   prev();
	}

	onMount(() => window.addEventListener('keydown', handleKey));
	onDestroy(() => { restoreEl(); window.removeEventListener('keydown', handleKey); });

	// ── Position helpers ────────────────────────────────────────────────────────

	// Border ring: sits on the element bounds, transparent fill, just a glowing border
	function highlightPos(rect: DOMRect | null): string {
		if (!rect) return 'display:none';
		return `left:${rect.left}px;top:${rect.top}px;width:${rect.width}px;height:${rect.height}px`;
	}

	// Tooltip position
	function tooltipPos(rect: DOMRect | null, pos: string): string {
		if (!rect || pos === 'center') {
			return `top:50%;left:50%;transform:translate(-50%,-50%)`;
		}
		const cx = rect.left + rect.width / 2;
		// clamp horizontal so tooltip stays on screen
		const clampedLeft = Math.min(Math.max(cx - TOOLTIP_W / 2, PAD), windowW - TOOLTIP_W - PAD);

		if (pos === 'top') {
			return `bottom:${windowH - rect.top + 14}px;left:${clampedLeft}px`;
		}
		if (pos === 'bottom') {
			return `top:${rect.bottom + 14}px;left:${clampedLeft}px`;
		}
		if (pos === 'right') {
			const top = Math.min(rect.top + rect.height / 2, windowH - 180);
			return `top:${top}px;left:${rect.right + 14}px;transform:translateY(-50%)`;
		}
		if (pos === 'left') {
			const top = Math.min(rect.top + rect.height / 2, windowH - 180);
			return `top:${top}px;right:${windowW - rect.left + 14}px;transform:translateY(-50%)`;
		}
		return '';
	}

	// Arrow direction (points TOWARD the target)
	function arrowClass(pos: string): string {
		if (pos === 'top')    return 'arrow-down';
		if (pos === 'bottom') return 'arrow-up';
		if (pos === 'right')  return 'arrow-left';
		if (pos === 'left')   return 'arrow-right';
		return '';
	}
</script>

{#if $showOmaTour}
	<!-- ── Backdrop ─────────────────────────────────────────────────────────── -->
	<div
		class="tour-backdrop"
		transition:fade={{ duration: 200 }}
		on:click|self={close}
		on:keydown={() => {}}
		role="dialog"
		aria-modal="true"
		aria-label="OMA Tour"
		tabindex="-1"
	>
		<!-- ── Gradient highlight on target element ─────────────────────────── -->
		{#if targetRect}
			<div class="tour-highlight" style={highlightPos(targetRect)}></div>
		{/if}

		<!-- ── Tooltip card ──────────────────────────────────────────────────── -->
		{#key currentStep}
			<div
				class="tour-tooltip {arrowClass(step.position)}"
				style="{tooltipPos(targetRect, step.position)};width:{TOOLTIP_W}px"
				transition:fly={{ y: 8, duration: 180 }}
			>
				<!-- Close -->
				<button class="tour-close" on:click={close} aria-label="Close tour">
					<XMark className="size-4" strokeWidth="2" />
				</button>

				<!-- Step counter -->
				<p class="tour-counter">{currentStep + 1} / {STEPS.length}</p>

				<!-- Content -->
				<h3 class="tour-title">{step.title}</h3>
				<p class="tour-desc">{step.description}</p>

				<!-- Dot indicators -->
				<div class="tour-dots">
					{#each STEPS as _, i}
						<button
							class="tour-dot {i === currentStep ? 'active' : ''}"
							on:click={() => { currentStep = i; }}
							aria-label="Go to step {i + 1}"
						></button>
					{/each}
				</div>

				<!-- Navigation -->
				<div class="tour-nav">
					<button class="tour-btn-ghost" on:click={prev} disabled={isFirst}>
						<ArrowLeft className="size-4" strokeWidth="2" />
						<span>Back</span>
					</button>
					<button class="tour-btn-primary" on:click={next}>
						<span>{isLast ? 'Done' : 'Next'}</span>
						{#if !isLast}
							<ArrowRight className="size-4" strokeWidth="2" />
						{/if}
					</button>
				</div>
			</div>
		{/key}
	</div>
{/if}

<style>
	/* ── Backdrop ─────────────────────────────────────────────────────────── */
	.tour-backdrop {
		position: fixed;
		inset: 0;
		z-index: 99990;
		background: rgba(0, 0, 0, 0.45);
	}

	/* ── Border ring — transparent fill, glowing outline around element ─────── */
	.tour-highlight {
		position: fixed;
		border-radius: 12px;
		background: transparent;
		border: 2px solid rgba(115, 178, 242, 0.9);
		box-shadow: 0 0 0 4px rgba(115, 178, 242, 0.12), 0 0 16px rgba(115, 178, 242, 0.35);
		pointer-events: none;
		z-index: 99993;
		animation: tour-pulse 2s ease-in-out infinite;
	}
	@keyframes tour-pulse {
		0%, 100% { box-shadow: 0 0 0 4px rgba(115, 178, 242, 0.12), 0 0 16px rgba(115, 178, 242, 0.35); }
		50%       { box-shadow: 0 0 0 6px rgba(115, 178, 242, 0.08), 0 0 24px rgba(115, 178, 242, 0.55); }
	}

	/* ── Tooltip ────────────────────────────────────────────────────────────── */
	.tour-tooltip {
		position: fixed;
		z-index: 99995;
		background: #0f172a;
		border: 1px solid rgba(255,255,255,0.08);
		border-radius: 14px;
		padding: 18px 18px 14px;
		box-shadow: 0 20px 60px rgba(0,0,0,0.5);
		color: #f1f5f9;
	}

	/* Arrows ── CSS triangle pointing toward target */
	.tour-tooltip.arrow-down::after {
		content: '';
		position: absolute;
		bottom: -8px;
		left: 50%;
		transform: translateX(-50%);
		border: 8px solid transparent;
		border-bottom: 0;
		border-top-color: #0f172a;
	}
	.tour-tooltip.arrow-up::after {
		content: '';
		position: absolute;
		top: -8px;
		left: 50%;
		transform: translateX(-50%);
		border: 8px solid transparent;
		border-top: 0;
		border-bottom-color: #0f172a;
	}
	.tour-tooltip.arrow-left::after {
		content: '';
		position: absolute;
		top: 50%;
		left: -8px;
		transform: translateY(-50%);
		border: 8px solid transparent;
		border-left: 0;
		border-right-color: #0f172a;
	}
	.tour-tooltip.arrow-right::after {
		content: '';
		position: absolute;
		top: 50%;
		right: -8px;
		transform: translateY(-50%);
		border: 8px solid transparent;
		border-right: 0;
		border-left-color: #0f172a;
	}

	/* ── Tooltip internals ──────────────────────────────────────────────────── */
	.tour-close {
		position: absolute;
		top: 12px;
		right: 12px;
		color: #64748b;
		background: none;
		border: none;
		cursor: pointer;
		padding: 2px;
		border-radius: 4px;
		display: flex;
		align-items: center;
		transition: color 0.15s;
	}
	.tour-close:hover { color: #f1f5f9; }

	.tour-counter {
		font-size: 11px;
		font-weight: 600;
		color: #73B2F2;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		margin-bottom: 6px;
	}

	.tour-title {
		font-size: 15px;
		font-weight: 700;
		color: #f1f5f9;
		margin: 0 0 8px;
		padding-right: 20px;
	}

	.tour-desc {
		font-size: 13px;
		line-height: 1.55;
		color: #94a3b8;
		margin: 0 0 14px;
	}

	/* Step dots */
	.tour-dots {
		display: flex;
		gap: 5px;
		justify-content: center;
		margin-bottom: 14px;
	}
	.tour-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #334155;
		border: none;
		cursor: pointer;
		padding: 0;
		transition: background 0.2s, transform 0.2s;
	}
	.tour-dot.active {
		background: #73B2F2;
		transform: scale(1.3);
	}
	.tour-dot:hover:not(.active) { background: #475569; }

	/* Navigation buttons */
	.tour-nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		border-top: 1px solid rgba(255,255,255,0.06);
		padding-top: 12px;
	}

	.tour-btn-ghost {
		display: flex;
		align-items: center;
		gap: 4px;
		font-size: 13px;
		font-weight: 500;
		color: #64748b;
		background: none;
		border: none;
		cursor: pointer;
		padding: 6px 8px;
		border-radius: 8px;
		transition: color 0.15s, background 0.15s;
	}
	.tour-btn-ghost:hover:not(:disabled) { color: #f1f5f9; background: rgba(255,255,255,0.06); }
	.tour-btn-ghost:disabled { opacity: 0.3; cursor: default; }

	.tour-btn-primary {
		display: flex;
		align-items: center;
		gap: 5px;
		font-size: 13px;
		font-weight: 600;
		color: #fff;
		background: linear-gradient(135deg, #003877 0%, #1a5db5 100%);
		border: none;
		border-radius: 8px;
		padding: 7px 14px;
		cursor: pointer;
		transition: opacity 0.15s, transform 0.1s;
	}
	.tour-btn-primary:hover { opacity: 0.9; transform: scale(1.02); }
	.tour-btn-primary:active { transform: scale(0.98); }
</style>
