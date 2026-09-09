<!-- ---------------------------------------------------------------------------
  File:        OmaRotatingHint.svelte
  Description: Rotating sentence hints on the OMA home page — cycles through
               O&M capability sentences with keyword highlights and slide animation.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';

	const i18n = getContext('i18n');

	type Hint = { pre: string; kw: string; post: string };

	$: HINTS = [
		{ pre: $i18n.t('Query open '), kw: $i18n.t('tickets and defects'), post: $i18n.t(' across all your plants instantly.') },
		{ pre: $i18n.t('Detect '), kw: $i18n.t('recurring fault patterns'), post: $i18n.t(' before they impact yield.') },
		{ pre: $i18n.t('Ask anything about '), kw: $i18n.t('inverter performance'), post: $i18n.t(' and get answers in seconds.') },
		{ pre: $i18n.t('Search '), kw: $i18n.t('contracts, manuals and project files'), post: $i18n.t(' by conversation.') },
		{ pre: $i18n.t('Cross-reference '), kw: $i18n.t('alarms'), post: $i18n.t(' with maintenance records for rapid root-cause analysis.') },
		{ pre: $i18n.t('Track '), kw: $i18n.t('repair orders, cleaning logs and shutdown schedules'), post: $i18n.t(' in one place.') },
		{ pre: $i18n.t('Get '), kw: $i18n.t('source-cited answers'), post: $i18n.t(' from your entire document library.') },
		{ pre: $i18n.t('Monitor '), kw: $i18n.t('live plant alarms'), post: $i18n.t(' and historical events side by side.') }
	] satisfies Hint[];

	let index = 0;
	let visible = true;
	let timer: ReturnType<typeof setInterval>;

	onMount(() => {
		timer = setInterval(() => {
			visible = false;
			setTimeout(() => {
				index = (index + 1) % HINTS.length;
				visible = true;
			}, 350);
		}, 4000);
	});

	onDestroy(() => clearInterval(timer));

	$: hint = HINTS[index];
</script>

<div class="hint-wrap" aria-live="polite">
	<p class="hint-text" class:visible>
		{hint.pre}<span class="hint-kw">{hint.kw}</span>{hint.post}
	</p>
</div>

<style>
	.hint-wrap {
		width: 100%;
		max-width: 580px;
		margin: 0 auto;
		height: 52px;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.hint-text {
		font-size: 14.5px;
		font-weight: 300;
		line-height: 1.6;
		color: #64748b;
		text-align: center;
		margin: 0;
		opacity: 0;
		transform: translateY(14px);
		transition: opacity 0.35s ease, transform 0.35s ease;
	}

	:global(.dark) .hint-text {
		color: #64748b;
	}

	.hint-text.visible {
		opacity: 1;
		transform: translateY(0);
	}

	.hint-kw {
		font-weight: 700;
		color: #73B2F2;
		margin: 0 3px;
	}
</style>
