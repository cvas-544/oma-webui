<!-- ---------------------------------------------------------------------------
  File:        OmaWelcomeModal.svelte
  Description: First-login welcome carousel — 5 screens with Enerparc imagery,
               dot indicators, and a round next arrow. Shows once per browser.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { showOmaWelcome } from '$lib/stores/omaWelcome';
	import { showOmaTour } from '$lib/stores/omaTour';
	import ArrowRightCircle from '$lib/components/icons/ArrowRightCircle.svelte';

	const STORAGE_KEY = 'oma_welcome_shown';

	type Slide = {
		image: string;
		title: string;
		subtitle: string;
		body: string;
	};

	const SLIDES: Slide[] = [
		{
			image: '/oma-welcome-bg-01.png',
			title: 'Welcome to OMA Agent',
			subtitle: 'Your AI-powered O&M assistant for Enerparc solar plant operations.',
			body: 'Ask anything in plain language across tickets, alarms, and documents, powered by live operational data and built for O&M engineers, asset managers, and site teams.'
		},
		{
			image: '/oma-login-bg-01.png',
			title: 'Operational Intelligence',
			subtitle: 'Full visibility into every maintenance event across your plants.',
			body: 'Instantly query open tickets, defects, repair orders, component replacements, cleaning records, shutdown schedules, and inverter metadata in one conversation.'
		},
		{
			image: '/oma-welcome-bg-03.png',
			title: 'Alarm Monitoring',
			subtitle: 'Stay ahead of faults before they impact yield.',
			body: 'Access live and historical plant alarms, identify recurring fault patterns, and cross-reference events with operational records for rapid root-cause analysis.'
		},
		{
			image: '/oma-welcome-bg-04.png',
			title: 'Document Intelligence',
			subtitle: 'Your entire knowledge base, searchable by conversation.',
			body: 'Ask questions across technical manuals, contracts, and project files and get source-cited answers drawn directly from your document library.'
		},
		{
			image: '/oma-login-bg-02.png',
			title: 'What\'s Coming Next',
			subtitle: 'OMA Agent is continuously expanding its capabilities.',
			body: 'Coming soon: Digital Twin yield-loss analytics, inverter error code diagnostics with guided resolution steps, and communication alarm monitoring.'
		}
	];

	let current = 0;
	$: isLast = current === SLIDES.length - 1;
	$: slide = SLIDES[current];

	// preload next image
	$: if (typeof window !== 'undefined' && current < SLIDES.length - 1) {
		const img = new Image();
		img.src = SLIDES[current + 1].image;
	}

	let animDir = 1; // 1 = forward, -1 = backward
	let animating = false;

	function goTo(i: number) {
		if (animating || i === current) return;
		animDir = i > current ? 1 : -1;
		current = i;
	}

	function next() {
		if (isLast) { dismiss(); return; }
		animDir = 1;
		current++;
	}

	function dismiss() {
		localStorage.setItem(STORAGE_KEY, '1');
		showOmaWelcome.set(false);
	}

	function startTour() {
		dismiss();
		showOmaTour.set(true);
	}

	onMount(() => {
		if (!localStorage.getItem(STORAGE_KEY)) {
			showOmaWelcome.set(true);
		}
	});

	function handleKey(e: KeyboardEvent) {
		if (!$showOmaWelcome) return;
		if (e.key === 'ArrowRight' || e.key === 'Enter') next();
		if (e.key === 'ArrowLeft' && current > 0) { animDir = -1; current--; }
		if (e.key === 'Escape') dismiss();
	}
</script>

<svelte:window on:keydown={handleKey} />

<!-- SVG distortion filter for liquid glass — hidden, referenced by CSS -->
<svg style="display:none" aria-hidden="true">
	<filter id="glass-distortion" x="0%" y="0%" width="100%" height="100%" filterUnits="objectBoundingBox">
		<feTurbulence type="fractalNoise" baseFrequency="0.001 0.005" numOctaves="1" seed="17" result="turbulence" />
		<feComponentTransfer in="turbulence" result="mapped">
			<feFuncR type="gamma" amplitude="1" exponent="10" offset="0.5" />
			<feFuncG type="gamma" amplitude="0" exponent="1" offset="0" />
			<feFuncB type="gamma" amplitude="0" exponent="1" offset="0.5" />
		</feComponentTransfer>
		<feGaussianBlur in="turbulence" stdDeviation="3" result="softMap" />
		<feSpecularLighting in="softMap" surfaceScale="5" specularConstant="1" specularExponent="100" lighting-color="white" result="specLight">
			<fePointLight x="-200" y="-200" z="300" />
		</feSpecularLighting>
		<feComposite in="specLight" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="litImage" />
		<feDisplacementMap in="SourceGraphic" in2="softMap" scale="200" xChannelSelector="R" yChannelSelector="G" />
	</filter>
</svg>

{#if $showOmaWelcome}
	<div
		class="welcome-backdrop"
		transition:fade={{ duration: 250 }}
		on:click|self={dismiss}
		on:keydown={() => {}}
		role="dialog"
		aria-modal="true"
		aria-label="Welcome to OMA Agent"
		tabindex="-1"
	>
		<div class="welcome-card">

			<!-- ── Hero image ───────────────────────────────────────────────── -->
			{#key current}
				<div
					class="welcome-hero"
					style="background-image: url('{slide.image}')"
					in:fade={{ duration: 400, easing: cubicOut }}
				>
					<div class="hero-overlay"></div>
				<!-- liquid glass layers -->
				<div class="glass-l1"></div>
				<div class="glass-l2"></div>
					<!-- Enerparc logo top-left -->
					<img
						src="/oma-welcome-logo.png"
						class="hero-logo"
						alt="Enerparc"
						draggable="false"
					/>
				</div>
			{/key}

			<!-- ── Content ──────────────────────────────────────────────────── -->
			<div class="welcome-body">
				{#key current}
					<div class="slide-content" in:fade={{ duration: 300, delay: 80 }}>
						<h2 class="welcome-title">{slide.title}</h2>
						<p class="welcome-sub">{slide.subtitle}</p>
						<p class="welcome-body-text">{slide.body}</p>
					</div>
				{/key}

				<!-- ── Footer: dots + [back + next] ────────────────────────── -->
				<div class="welcome-footer">
					<!-- Dot indicators -->
					<div class="dots">
						{#each SLIDES as _, i}
							<button
								class="dot {i === current ? 'active' : ''}"
								on:click={() => goTo(i)}
								aria-label="Go to slide {i + 1}"
							></button>
						{/each}
					</div>

					<!-- Right side: back + next/last actions -->
					<div class="footer-right">
						<button
							class="btn-back"
							on:click={() => { if (current > 0) { animDir = -1; current--; } }}
							disabled={current === 0}
							aria-label="Previous slide"
						>
							<ArrowRightCircle className="size-8" strokeWidth="1.5" />
						</button>

						{#if isLast}
							<div class="last-actions">
								<button class="btn-tour" on:click={startTour}>Take a Tour</button>
								<button class="btn-start" on:click={dismiss}>Get Started</button>
							</div>
						{:else}
							<button class="btn-next" on:click={next} aria-label="Next slide">
								<ArrowRightCircle className="size-8" strokeWidth="1.5" />
							</button>
						{/if}
					</div>
				</div>
			</div>

		</div>
	</div>
{/if}

<style>
	/* ── Backdrop ────────────────────────────────────────────────────────── */
	.welcome-backdrop {
		position: fixed;
		inset: 0;
		z-index: 99998;
		background: rgba(0, 0, 0, 0.52);
		backdrop-filter: blur(6px);
		-webkit-backdrop-filter: blur(6px);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	/* ── Card ────────────────────────────────────────────────────────────── */
	.welcome-card {
		width: 676px;
		border-radius: 20px;
		overflow: hidden;
		background: rgba(8, 16, 32, 0.72);
		backdrop-filter: blur(28px) saturate(1.5);
		-webkit-backdrop-filter: blur(28px) saturate(1.5);
		border: 1px solid rgba(115, 178, 242, 0.16);
		box-shadow:
			0 40px 90px rgba(0, 0, 0, 0.60),
			0 0 0 1px rgba(255, 255, 255, 0.04) inset;
	}

	/* ── Hero image zone ─────────────────────────────────────────────────── */
	.welcome-hero {
		position: relative;
		height: 320px;
		background-size: cover;
		background-position: center;
		display: flex;
		align-items: flex-end;
		overflow: hidden;
	}

	.hero-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(
			to bottom,
			rgba(0, 20, 50, 0.15) 0%,
			rgba(0, 10, 30, 0.60) 100%
		);
	}

	/* liquid glass — layer 1: SVG distortion only */
	.glass-l1 {
		position: absolute;
		inset: 0;
		z-index: 1;
		filter: url(#glass-distortion);
		isolation: isolate;
		pointer-events: none;
	}

	/* liquid glass — layer 2: white tint */
	.glass-l2 {
		position: absolute;
		inset: 0;
		z-index: 2;
		background: rgba(255, 255, 255, 0.04);
		pointer-events: none;
	}

	.hero-logo {
		position: absolute;
		top: 18px;
		left: 22px;
		height: 28px;
		width: auto;
		filter: none;
		z-index: 4;
		user-select: none;
	}

	/* ── Body ────────────────────────────────────────────────────────────── */
	.welcome-body {
		padding: 24px 28px 22px;
		display: flex;
		flex-direction: column;
		gap: 18px;
		height: 250px;
	}

	.slide-content {
		flex: 1;
		overflow: hidden;
	}

	.welcome-title {
		font-size: 17px;
		font-weight: 700;
		color: #f1f5f9;
		letter-spacing: -0.015em;
		margin: 0 0 6px;
	}

	.welcome-sub {
		font-size: 13px;
		line-height: 1.55;
		color: #73B2F2;
		margin: 0 0 14px;
		font-weight: 500;
	}

	.welcome-body-text {
		font-size: 13px;
		line-height: 1.65;
		color: #94a3b8;
		margin: 0;
	}

	/* ── Footer ──────────────────────────────────────────────────────────── */
	.welcome-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-top: 1px solid rgba(255, 255, 255, 0.07);
		padding-top: 14px;
	}

	/* Dots */
	.dots {
		display: flex;
		gap: 6px;
		align-items: center;
	}

	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.2);
		border: none;
		padding: 0;
		cursor: pointer;
		transition: background 0.2s, transform 0.2s, width 0.25s;
	}

	.dot.active {
		background: #73B2F2;
		transform: scale(1.25);
		width: 18px;
		border-radius: 3px;
	}

	.footer-right {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	/* Back arrow button */
	.btn-back {
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		color: #64748b;
		display: flex;
		align-items: center;
		transform: rotate(180deg);
		transition: color 0.15s;
	}
	.btn-back:hover:not(:disabled) { color: #94a3b8; }
	.btn-back:disabled { opacity: 0.2; cursor: default; }

	/* Next arrow button */
	.btn-next {
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		color: #73B2F2;
		display: flex;
		align-items: center;
		transition: color 0.15s, transform 0.15s;
	}
	.btn-next:hover { color: #a8d0f7; transform: translateX(2px); }

	/* Last slide actions */
	.last-actions {
		display: flex;
		gap: 8px;
	}

	.btn-tour {
		padding: 8px 16px;
		border-radius: 8px;
		background: linear-gradient(135deg, #003877 0%, #1a5db5 100%);
		color: #fff;
		font-size: 13px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: opacity 0.15s;
	}
	.btn-tour:hover { opacity: 0.88; }

	.btn-start {
		padding: 8px 16px;
		border-radius: 8px;
		background: rgba(255, 255, 255, 0.07);
		color: #94a3b8;
		font-size: 13px;
		font-weight: 500;
		border: 1px solid rgba(255, 255, 255, 0.10);
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
	}
	.btn-start:hover { background: rgba(255, 255, 255, 0.12); color: #e2e8f0; }
</style>
