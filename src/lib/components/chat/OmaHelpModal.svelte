<!-- ---------------------------------------------------------------------------
  File:        OmaHelpModal.svelte
  Description: OMA Help & Support modal — two-column layout (brand image left,
               ticket form right). Supports screen capture attachment.
               Submits to VITE_OMA_FEEDBACK_URL if set.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { showOmaHelp } from '$lib/stores/omaHelp';

	const i18n: any = getContext('i18n');

	const HELP_URL: string = import.meta.env.VITE_OMA_FEEDBACK_URL ?? '';

	const categories = [
		'Bug Report',
		'Feature Request',
		'Access Issue',
		'Agent Reasoning / Data Problem',
		'Other'
	];

	let category = '';
	let message = '';
	let screenshot: string | null = null;
	let screenshotName = '';
	let sent = false;
	let loading = false;
	let fileInput: HTMLInputElement;

	// ── File attach ───────────────────────────────────────────────────────────
	function onFileChange(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		screenshotName = file.name;
		const reader = new FileReader();
		reader.onload = (ev) => { screenshot = ev.target?.result as string; };
		reader.readAsDataURL(file);
	}

	function removeScreenshot() {
		screenshot = null;
		screenshotName = '';
		if (fileInput) fileInput.value = '';
	}

	// ── Submit ────────────────────────────────────────────────────────────────
	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!category || message.trim().length < 10) return;
		loading = true;
		try {
			if (HELP_URL) {
				await fetch(HELP_URL, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ type: 'help', category, message, screenshot })
				});
			}
			sent = true;
		} catch {
			toast.error($i18n.t('Failed to send. Please try again.'));
		} finally {
			loading = false;
		}
	}

	function reset() {
		category = '';
		message = '';
		screenshot = null;
		screenshotName = '';
		sent = false;
	}

	function close() {
		showOmaHelp.set(false);
		reset();
	}
</script>

{#if $showOmaHelp}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
		on:click|self={close}
		on:keydown={(e) => e.key === 'Escape' && close()}
		role="dialog"
		tabindex="-1"
		aria-modal="true"
		aria-label={$i18n.t('Help & Support')}
	>
		<!-- Modal card -->
		<div class="relative flex w-full max-w-3xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-gray-900">

			<!-- ── Close button ────────────────────────────────────────────────── -->
			<button
				class="absolute right-3 top-3 z-10 flex size-7 items-center justify-center rounded-full text-white/70 transition hover:bg-white/10 hover:text-white"
				on:click={close}
				aria-label={$i18n.t('Close')}
				type="button"
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
				</svg>
			</button>

			<!-- ── LEFT: brand panel ───────────────────────────────────────────── -->
			<div class="relative hidden w-[42%] flex-shrink-0 md:block">
				<img
					src="/oma-help-bg.png"
					alt="Enerparc solar plant"
					class="h-full w-full object-cover"
				/>
				<!-- Dark overlay for text legibility across the full panel -->
				<div class="absolute inset-0 bg-[#003877]/65"></div>
				<div class="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/40"></div>

				<div class="absolute inset-0 flex flex-col justify-between p-7">
					<div>
						<p class="mb-2 text-[0.65rem] font-semibold uppercase tracking-widest text-white/80">
							O&amp;M AIssistant
						</p>
						<h2 class="text-2xl font-bold leading-tight text-white">
							{$i18n.t('Help &')}<br />{$i18n.t('Support')}
						</h2>
						<p class="mt-3 text-xs leading-relaxed text-white/90">
							{$i18n.t("Something not right? Let us know and we'll get back to you.")}
						</p>
					</div>

					<p class="text-[0.6rem] text-white/70">
						{$i18n.t('Enerparc · O&M AIssistant')}
					</p>
				</div>
			</div>

			<!-- ── RIGHT: form panel ──────────────────────────────────────────── -->
			<div class="flex flex-1 flex-col p-7">
				{#if sent}
					<!-- Success state -->
					<div class="flex flex-1 flex-col items-center justify-center gap-4 text-center">
						<div class="flex size-12 items-center justify-center rounded-full bg-emerald-500/10">
							<svg xmlns="http://www.w3.org/2000/svg" class="size-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
								<path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
							</svg>
						</div>
						<div>
							<p class="font-semibold text-gray-900 dark:text-white">{$i18n.t('Ticket submitted!')}</p>
							<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
								{$i18n.t("We'll get back to you as soon as possible.")}
							</p>
						</div>
						<button
							on:click={reset}
							type="button"
							class="rounded-lg border border-gray-200 px-4 py-1.5 text-xs text-gray-600 transition hover:border-gray-400 dark:border-white/10 dark:text-gray-400 dark:hover:border-white/30"
						>
							{$i18n.t('Submit another')}
						</button>
					</div>
				{:else}
					<form class="flex flex-col gap-5" on:submit={handleSubmit}>
						<!-- Category pills -->
						<div class="flex flex-col gap-2">
							<p class="text-[0.75rem] font-medium text-gray-700 dark:text-gray-300">
								{$i18n.t('Category')}
							</p>
							<div class="flex flex-wrap gap-1.5">
								{#each categories as c}
									<button
										type="button"
										on:click={() => (category = c)}
										class="rounded-full border px-3 py-1 text-xs transition-colors {category === c
											? 'border-[#003877] bg-[#003877] text-white dark:border-[#73B2F2] dark:bg-[#73B2F2]/20 dark:text-[#73B2F2]'
											: 'border-gray-200 bg-white text-gray-500 hover:border-gray-400 dark:border-white/10 dark:bg-white/5 dark:text-gray-400 dark:hover:border-white/30'}"
									>
										{$i18n.t(c)}
									</button>
								{/each}
							</div>
						</div>

						<!-- Attach screenshot -->
						<div class="flex flex-col gap-2">
							<p class="text-[0.75rem] font-medium text-gray-700 dark:text-gray-300">
								{$i18n.t('Screenshot')} <span class="font-normal text-gray-400">{$i18n.t('(optional)')}</span>
							</p>
							<!-- Hidden file input -->
							<input
								bind:this={fileInput}
								type="file"
								accept="image/*"
								class="hidden"
								on:change={onFileChange}
							/>
							{#if screenshot}
								<div class="flex items-center gap-3">
									<img
										src={screenshot}
										alt="Attached screenshot"
										class="max-h-24 max-w-[140px] rounded-lg border border-gray-200 object-cover dark:border-white/10"
									/>
									<div class="flex flex-col gap-1">
										<p class="max-w-[140px] truncate text-[0.7rem] text-gray-500 dark:text-gray-400">{screenshotName}</p>
										<button
											type="button"
											on:click={removeScreenshot}
											class="flex items-center gap-1 text-[0.7rem] text-red-500 hover:text-red-600"
										>
											<svg xmlns="http://www.w3.org/2000/svg" class="size-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
												<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
											</svg>
											{$i18n.t('Remove')}
										</button>
									</div>
								</div>
							{:else}
								<button
									type="button"
									on:click={() => fileInput.click()}
									class="flex items-center gap-2 rounded-lg border border-dashed border-gray-300 px-3 py-2.5 text-xs text-gray-500 transition hover:border-[#003877] hover:text-[#003877] dark:border-white/10 dark:text-gray-400 dark:hover:border-[#73B2F2] dark:hover:text-[#73B2F2]"
								>
									<svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
										<path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.552 18.32m.009-.01-.01.01m5.699-9.941-7.81 7.81a1.5 1.5 0 0 0 2.112 2.13" />
									</svg>
									{$i18n.t('Attach screenshot')}
								</button>
							{/if}
						</div>

						<!-- Message -->
						<div class="flex flex-col gap-2">
							<label class="text-[0.75rem] font-medium text-gray-700 dark:text-gray-300" for="oma-help-message">
								{$i18n.t('Message')}
							</label>
							<textarea
								id="oma-help-message"
								bind:value={message}
								placeholder={$i18n.t('Describe your issue in detail…')}
								rows="4"
								maxlength="500"
								required
								minlength="10"
								class="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 outline-none transition focus:border-[#003877] focus:ring-1 focus:ring-[#003877] dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-gray-600 dark:focus:border-[#73B2F2] dark:focus:ring-[#73B2F2]"
							></textarea>
							<p class="text-right text-[0.7rem] text-gray-400">{message.length} / 500</p>
						</div>

						<!-- Submit -->
						<button
							type="submit"
							disabled={!category || message.trim().length < 10 || loading}
							class="flex items-center justify-center gap-2 rounded-xl bg-[#003877] py-2.5 text-sm font-medium text-white transition hover:bg-[#002a63] disabled:cursor-not-allowed disabled:opacity-40 dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] dark:hover:bg-[#73B2F2]/30"
						>
							{#if loading}
								<svg class="size-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
								</svg>
							{/if}
							{$i18n.t('Submit Ticket')}
						</button>
					</form>
				{/if}
			</div>
		</div>
	</div>
{/if}
