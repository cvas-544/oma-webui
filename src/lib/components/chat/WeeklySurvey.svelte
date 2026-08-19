<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        WeeklySurvey.svelte
	// Description: Periodic feedback widget — fixed 320×400 shell, content slides
	//              inside. invite → questions → thank you.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { user } from '$lib/stores';

	$: firstName = $user?.name?.split(' ')[0] ?? '';

	const COOLDOWN_DAYS = 7;
	const SNOOZE_DAYS   = 3;
	const SHOW_DELAY_MS = 2000; // TODO: revert to 8000 before deploy

	const BG_IMAGES = ['/oma-login-bg-01.png', '/oma-login-bg-03.png'];
	const bgImage   = BG_IMAGES[Math.floor(Math.random() * BG_IMAGES.length)];

	type QType = 'stars' | 'choice' | 'text' | 'slider';
	interface Question {
		text: string;
		type: QType;
		hint?: string;
		options?: string[];
		skippable?: boolean;
		min?: number;
		max?: number;
		minLabel?: string;
		maxLabel?: string;
	}

	const QUESTIONS: Question[] = [
		{ text: 'How satisfied are you with OMA Agent this week?', type: 'stars', hint: 'TAP A STAR' },
		{ text: 'Did the agent give you accurate plant data?', type: 'choice', hint: 'SELECT ONLY ONE', options: ['Yes', 'Mostly', 'No'] },
		{ text: 'How likely are you to recommend OMA Agent to a colleague?', type: 'slider', min: 0, max: 10, minLabel: 'Not likely', maxLabel: 'Very likely' },
		{ text: 'What would you most like to improve?', type: 'text', skippable: true }
	];

	let visible  = false;
	let stage: 'invite' | 'questions' | 'done' = 'invite';
	let currentQ = 0;
	let direction = 1;
	let answers: Record<number, any> = {};
	let textDraft = '';
	let hoverStar = 0;
	let sliderValue = 5;

	$: q          = QUESTIONS[currentQ];
	$: canProceed = answers[currentQ] !== undefined || q?.skippable || q?.type === 'slider';
	$: isLast     = currentQ === QUESTIONS.length - 1;
	$: activeStar = hoverStar || (answers[currentQ] ?? 0);
	$: sliderFill = ((sliderValue - (q?.min ?? 0)) / ((q?.max ?? 10) - (q?.min ?? 0))) * 100;

	function daysSince(key: string) {
		const raw = localStorage.getItem(key);
		return raw ? (Date.now() - Number(raw)) / 86400000 : Infinity;
	}

	onMount(() => {
		const ok =
			daysSince('inv_survey_last_completed') >= COOLDOWN_DAYS &&
			daysSince('inv_survey_dismissed_at')   >= SNOOZE_DAYS   &&
			daysSince('inv_survey_last_shown')      >= COOLDOWN_DAYS;
		if (!ok) return;
		const t = setTimeout(() => {
			localStorage.setItem('inv_survey_last_shown', String(Date.now()));
			visible = true;
		}, SHOW_DELAY_MS);
		return () => clearTimeout(t);
	});

	function dismiss() { visible = false; }
	function snooze()  { localStorage.setItem('inv_survey_dismissed_at', String(Date.now())); visible = false; }

	function startSurvey() {
		direction = 1;
		answers = {};
		textDraft = '';
		currentQ = 0;
		stage = 'questions';
	}

	function next() {
		if (q.type === 'text' && textDraft.trim()) answers[currentQ] = textDraft.trim();
		if (q.type === 'slider') answers[currentQ] = sliderValue;
		if (isLast) { submit(); return; }
		direction = 1;
		currentQ++;
		textDraft = answers[currentQ] ?? '';
		if (QUESTIONS[currentQ]?.type === 'slider') sliderValue = answers[currentQ] ?? 5;
	}

	function back() {
		if (currentQ === 0) return;
		direction = -1;
		currentQ--;
		textDraft = answers[currentQ] ?? '';
	}

	function pick(value: any) { answers = { ...answers, [currentQ]: value }; }

	function submit() {
		localStorage.setItem('inv_survey_last_completed', String(Date.now()));
		console.log('[WeeklySurvey] answers:', answers);
		stage = 'done';
		setTimeout(() => { visible = false; }, 2800);
	}
</script>

{#if visible}
	<!-- Fixed shell — never resizes, slides in once on mount -->
	<div
		class="fixed bottom-6 right-6 z-[200] w-[320px] h-[400px] rounded-2xl overflow-hidden shadow-2xl"
		transition:fly={{ y: 36, duration: 380, easing: cubicOut }}
	>

		<!-- ── INVITE ──────────────────────────────────────────────────────── -->
		{#if stage === 'invite'}
			<div
				class="absolute inset-0"
				in:fly={{ x: -40, duration: 280, easing: cubicOut }}
				out:fly={{ x: -40, duration: 220, easing: cubicOut }}
			>
				<img src={bgImage} alt="" class="absolute inset-0 h-full w-full object-cover" aria-hidden="true" />
				<div class="absolute inset-0" style="background: linear-gradient(to bottom, rgba(0,56,119,0.25) 0%, rgba(0,56,119,0.55) 45%, rgba(0,56,119,0.92) 100%);"></div>

				<div class="relative z-10 flex flex-col h-full p-5">
					<div class="flex items-center justify-between">
						<span class="text-[10px] font-semibold uppercase tracking-[0.14em] text-white" style="text-shadow:0 1px 4px rgba(0,0,0,0.4);">
							Weekly Feedback
						</span>
						<button on:click={dismiss} class="flex items-center justify-center w-6 h-6 rounded-full text-white/70 hover:text-white hover:bg-white/10 transition-colors" aria-label="Close">
							<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
						</button>
					</div>

					<div class="flex-1"></div>

					<div class="flex flex-col gap-3">
						<div>
							<h3 class="text-[18px] font-semibold text-white leading-snug">How is OMA Agent working for you?</h3>
							<p class="text-[12px] text-white/60 mt-1">2 min &nbsp;·&nbsp; {QUESTIONS.length} questions</p>
						</div>
						<div class="flex flex-col gap-2 mt-1">
							<button on:click={startSurvey} class="w-full rounded-xl bg-white py-2.5 text-[13px] font-semibold text-[#003877] transition hover:bg-white/90 active:scale-[0.98]">
								Take a Survey
							</button>
							<button on:click={snooze} class="w-full rounded-xl border border-white/40 py-2.5 text-[13px] font-medium text-white/80 transition hover:border-white/70 hover:text-white active:scale-[0.98]">
								Remind me later
							</button>
						</div>
					</div>
				</div>
			</div>

		<!-- ── QUESTIONS ───────────────────────────────────────────────────── -->
		{:else if stage === 'questions'}
			<div
				class="absolute inset-0 bg-white flex flex-col"
				in:fly={{ x: 40, duration: 280, easing: cubicOut }}
				out:fly={{ x: 40, duration: 220, easing: cubicOut }}
			>
				<!-- Progress + close -->
				<div class="flex items-center gap-1.5 px-5 pt-5 pb-2 shrink-0">
					{#each QUESTIONS as _, i}
						<div
							class="h-2 rounded-full transition-all duration-300"
							style="width:{i === currentQ ? '2rem' : '0.5rem'}; background-color:{i <= currentQ ? '#003877' : '#e4e4e7'};"
						></div>
					{/each}
					<div class="flex-1"></div>
					<button on:click={dismiss} class="flex items-center justify-center w-6 h-6 rounded-full text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 transition-colors" aria-label="Close">
						<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
					</button>
				</div>

				<!-- Sliding question content — relative wrapper clips the slide -->
				<div class="flex-1 relative overflow-hidden">
				{#key currentQ}
					<div
						class="absolute inset-0 px-5 pt-2 overflow-y-auto"
						in:fly={{ x: direction * 50, duration: 260, easing: cubicOut }}
						out:fly={{ x: -direction * 50, duration: 200, easing: cubicOut }}
					>
						<p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-zinc-400 mb-1">
							Question {String(currentQ + 1).padStart(2, '0')}
						</p>
						<h3 class="text-[15px] font-semibold text-zinc-800 leading-snug mb-4">{q.text}</h3>

						<!-- STARS -->
						{#if q.type === 'stars'}
							{#if q.hint}<p class="text-[9px] font-semibold uppercase tracking-[0.12em] text-zinc-400 mb-3">{q.hint}</p>{/if}
							<div class="flex gap-2" on:mouseleave={() => (hoverStar = 0)}>
								{#each [1,2,3,4,5] as star}
									<button class="transition-transform hover:scale-110 active:scale-95" on:click={() => pick(star)} on:mouseenter={() => (hoverStar = star)} aria-label="Rate {star}">
										<svg class="w-9 h-9" viewBox="0 0 24 24" fill={star <= activeStar ? '#003877' : 'none'} stroke={star <= activeStar ? '#003877' : '#d4d4d8'} stroke-width="1.5">
											<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
										</svg>
									</button>
								{/each}
							</div>

						<!-- CHOICE -->
						{:else if q.type === 'choice'}
							{#if q.hint}<p class="text-[9px] font-semibold uppercase tracking-[0.12em] text-zinc-400 mb-3">{q.hint}</p>{/if}
							<div class="flex flex-col gap-3">
								{#each q.options ?? [] as option}
									{@const selected = answers[currentQ] === option}
									<button on:click={() => pick(option)} class="flex items-center gap-3 text-left group">
										<div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors {selected ? 'border-[#003877]' : 'border-zinc-300 group-hover:border-[#73B2F2]'}">
											{#if selected}<div class="w-2 h-2 rounded-full bg-[#003877]"></div>{/if}
										</div>
										<span class="text-[13px] transition-colors {selected ? 'text-zinc-800 font-medium' : 'text-zinc-500'}">{option}</span>
									</button>
								{/each}
							</div>

						<!-- TEXT -->
						{:else if q.type === 'text'}
							<textarea
								bind:value={textDraft}
								placeholder="Type your answer here..."
								rows="3"
								class="w-full resize-none rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-[13px] text-zinc-800 placeholder:text-zinc-400 focus:border-[#73B2F2] focus:outline-none transition-colors leading-relaxed"
							/>

						<!-- SLIDER -->
						{:else if q.type === 'slider'}
							<div class="flex flex-col gap-4 mt-2">
								<!-- Current value -->
								<div class="flex items-end gap-1">
									<span class="text-[42px] font-bold leading-none" style="color:#003877;">{sliderValue}</span>
									<span class="text-[13px] text-zinc-400 mb-1">/ {q.max ?? 10}</span>
								</div>

								<!-- Slider track -->
								<input
									type="range"
									min={q.min ?? 0}
									max={q.max ?? 10}
									step="1"
									bind:value={sliderValue}
									class="survey-slider w-full h-2 rounded-full appearance-none cursor-pointer outline-none"
									style="background: linear-gradient(to right, #003877 0%, #003877 {sliderFill}%, #e4e4e7 {sliderFill}%, #e4e4e7 100%);"
								/>

								<!-- Min / max labels -->
								<div class="flex justify-between text-[11px] text-zinc-400">
									<span>{q.minLabel ?? q.min ?? 0}</span>
									<span>{q.maxLabel ?? q.max ?? 10}</span>
								</div>
							</div>
						{/if}
					</div>
				{/key}
				</div><!-- end relative overflow-hidden wrapper -->

				<!-- Nav -->
				<div class="flex items-center justify-between px-5 py-4 shrink-0">
					<button on:click={back} disabled={currentQ === 0} class="text-[13px] text-zinc-400 hover:text-zinc-600 transition-colors disabled:opacity-0">
						Back
					</button>
					<button on:click={next} disabled={!canProceed} class="rounded-xl bg-[#003877] px-6 py-2.5 text-[13px] font-semibold text-white transition hover:bg-[#002a63] active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none">
						{isLast ? 'Submit' : 'Next'}
					</button>
				</div>
			</div>

		<!-- ── THANK YOU ─────────────────────────────────────────────────────── -->
		{:else if stage === 'done'}
			<div
				class="absolute inset-0 bg-white flex flex-col items-center justify-center gap-4 px-8 text-center"
				in:fly={{ x: 40, duration: 280, easing: cubicOut }}
			>
				<div class="flex items-center justify-center w-14 h-14 rounded-full" style="background-color:rgba(0,56,119,0.08);">
					<svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="#003877" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
						<polyline points="20 6 9 17 4 12"/>
					</svg>
				</div>
				<div>
					<h3 class="text-[18px] font-semibold text-zinc-800">
						Thank you{firstName ? `, ${firstName}` : ''}!
					</h3>
					<p class="text-[13px] text-zinc-400 leading-relaxed mt-1">Your feedback helps us improve OMA Agent for your team.</p>
				</div>
			</div>
		{/if}

	</div>
{/if}

<style>
	.survey-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 20px;
		height: 20px;
		border-radius: 50%;
		background: #003877;
		cursor: pointer;
		border: 2px solid white;
		box-shadow: 0 1px 4px rgba(0,56,119,0.35);
		transition: transform 0.15s ease;
	}
	.survey-slider::-webkit-slider-thumb:hover {
		transform: scale(1.2);
	}
	.survey-slider::-moz-range-thumb {
		width: 20px;
		height: 20px;
		border-radius: 50%;
		background: #003877;
		cursor: pointer;
		border: 2px solid white;
		box-shadow: 0 1px 4px rgba(0,56,119,0.35);
	}
</style>
