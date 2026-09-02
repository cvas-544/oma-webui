<!-- ---------------------------------------------------------------------------
  File:        OmaPromptLibrary.svelte
  Description: OMA Prompt Library modal — topic-filtered prompt browser with
               inline admin CRUD (add / edit / delete). Users can copy prompts
               or send them to the chat input. Admins manage prompts in-place.
  Author:      Vasu Chukka
  Co-author:   Claude Code
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { fade, slide } from 'svelte/transition';
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { showOmaPromptLibrary, omaPromptInsert } from '$lib/stores/omaPromptLibrary';
	import { user } from '$lib/stores';
	import Bookmark from '$lib/components/icons/Bookmark.svelte';

	const i18n: any = getContext('i18n');

	// ── Types ──────────────────────────────────────────────────────────────────

	type Prompt = {
		id: string;
		title: string;
		text: string;
		topic: string;
	};

	// ── Prompt data (localStorage-persisted) ───────────────────────────────────

	const DEFAULT_PROMPTS: Prompt[] = [
		// Performance
		{ id: 'p1', topic: 'Performance',    title: 'PR by park & month',          text: 'Show Performance Ratio (PR) for [park name] for [month / year].' },
		{ id: 'p2', topic: 'Performance',    title: 'Compare specific yield',       text: 'Compare specific yield of [park A] vs [park B] for [time period].' },
		{ id: 'p3', topic: 'Performance',    title: 'Inverter availability',        text: 'Which inverters had the lowest availability last week in [park name]?' },
		{ id: 'p4', topic: 'Performance',    title: 'Top underperformers',          text: 'Show me the top 5 underperforming parks this quarter.' },
		{ id: 'p5', topic: 'Performance',    title: 'Availability factor YTD',      text: 'What is the availability factor of [park name] year-to-date?' },
		// Faults & Alarms
		{ id: 'f1', topic: 'Faults & Alarms', title: 'Active alarms',              text: 'Show all active alarms for [park name].' },
		{ id: 'f2', topic: 'Faults & Alarms', title: 'Alarms last 7 days',         text: 'How many alarms were triggered in [park name] in the last 7 days?' },
		{ id: 'f3', topic: 'Faults & Alarms', title: 'Top recurring faults',       text: 'List the top 5 recurring fault types across all parks this month.' },
		{ id: 'f4', topic: 'Faults & Alarms', title: 'Most alarms by park',        text: 'Which park had the most alarms last week?' },
		{ id: 'f5', topic: 'Faults & Alarms', title: 'Critical alarms YTD',        text: 'Show me all critical alarms from [park name] this year.' },
		// Energy
		{ id: 'e1', topic: 'Energy',         title: 'Monthly production',           text: 'What was the total energy production for [park name] last month?' },
		{ id: 'e2', topic: 'Energy',         title: 'Energy loss breakdown',        text: 'Show energy loss breakdown for [park name] last quarter.' },
		{ id: 'e3', topic: 'Energy',         title: 'YoY production comparison',    text: 'Compare energy production of [park name] vs the same period last year.' },
		{ id: 'e4', topic: 'Energy',         title: 'Total across all parks',       text: 'What is the total energy production across all parks this year?' },
		{ id: 'e5', topic: 'Energy',         title: 'Daily production values',      text: 'Show me daily production values for [park name] this month.' },
		// Tickets
		{ id: 't1', topic: 'Tickets',        title: 'Open tickets by park',         text: 'Show all open tickets for [park name].' },
		{ id: 't2', topic: 'Tickets',        title: 'Tickets closed last month',    text: 'How many tickets were closed last month across all parks?' },
		{ id: 't3', topic: 'Tickets',        title: 'Park with most open tickets',  text: 'Which park has the most open tickets right now?' },
		{ id: 't4', topic: 'Tickets',        title: 'Overdue tickets',              text: 'Show me all overdue tickets across all parks.' },
		{ id: 't5', topic: 'Tickets',        title: 'Avg resolution time',          text: 'What is the average ticket resolution time for [park name]?' },
		// Plant Overview
		{ id: 'o1', topic: 'Plant Overview', title: 'Park status summary',          text: 'Give me a status summary of [park name] right now.' },
		{ id: 'o2', topic: 'Plant Overview', title: 'Installed capacity',           text: 'What is the installed capacity of [park name]?' },
		{ id: 'o3', topic: 'Plant Overview', title: 'All parks operational status', text: 'Show all parks and their current operational status.' },
		{ id: 'o4', topic: 'Plant Overview', title: 'Offline inverters',            text: 'How many inverters are currently offline across all parks?' },
		// Maintenance
		{ id: 'm1', topic: 'Maintenance',    title: 'Planned maintenance',          text: 'Are there any planned maintenance activities for [park name] this month?' },
		{ id: 'm2', topic: 'Maintenance',    title: 'Maintenance history',          text: 'Show maintenance history for [park name] over the last 6 months.' },
		{ id: 'm3', topic: 'Maintenance',    title: 'Preventive maintenance due',   text: 'What preventive maintenance is due next month for [park name]?' },
		// Reports
		{ id: 'r1', topic: 'Reports',        title: 'Monthly performance report',   text: 'Generate a monthly performance report for [park name].' },
		{ id: 'r2', topic: 'Reports',        title: 'Executive summary all parks',  text: 'Create an executive summary of all parks for [month].' },
		{ id: 'r3', topic: 'Reports',        title: 'Export to Excel',              text: 'Export production data for [park name] as Excel for last quarter.' },
		{ id: 'r4', topic: 'Reports',        title: 'Alarm summary report',         text: 'Generate an alarm summary report for [park name] last month.' },
	];

	const BASE_TOPICS = ['All', 'Performance', 'Faults & Alarms', 'Energy', 'Tickets', 'Plant Overview', 'Maintenance', 'Reports'];

	function loadTopics(): string[] {
		if (typeof localStorage === 'undefined') return BASE_TOPICS;
		try {
			const raw = localStorage.getItem('oma_custom_topics');
			const custom: string[] = raw ? JSON.parse(raw) : [];
			return [...BASE_TOPICS, ...custom.filter((t) => !BASE_TOPICS.includes(t))];
		} catch { return BASE_TOPICS; }
	}

	function saveCustomTopics(all: string[]) {
		const custom = all.filter((t) => t !== 'All' && !BASE_TOPICS.slice(1).includes(t));
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('oma_custom_topics', JSON.stringify(custom));
		}
	}

	function loadPrompts(): Prompt[] {
		if (typeof localStorage === 'undefined') return DEFAULT_PROMPTS;
		try {
			const raw = localStorage.getItem('oma_prompts');
			return raw ? JSON.parse(raw) : DEFAULT_PROMPTS;
		} catch { return DEFAULT_PROMPTS; }
	}

	function savePrompts(list: Prompt[]) {
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('oma_prompts', JSON.stringify(list));
		}
	}

	// ── State ──────────────────────────────────────────────────────────────────

	let prompts: Prompt[] = loadPrompts();
	let topics: string[] = loadTopics();
	let selectedTopic = 'All';
	let searchQuery = '';
	let showSaved = false;
	let adminMode = false;

	// Inline form state
	let editingId: string | null = null;
	let addingNew = false;
	let confirmDeleteId: string | null = null;

	let formTitle = '';
	let formText = '';
	let formTopic = topics[1];
	let newTopicName = '';

	let savedIds: Set<string> = new Set(
		JSON.parse(typeof localStorage !== 'undefined' ? (localStorage.getItem('oma_saved_prompts') ?? '[]') : '[]')
	);

	$: isAdmin = $user?.role === 'admin';

	$: filtered = prompts.filter((p) => {
		const matchTopic = selectedTopic === 'All' || p.topic === selectedTopic;
		const matchSearch =
			searchQuery.trim() === '' ||
			p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
			p.text.toLowerCase().includes(searchQuery.toLowerCase());
		const matchSaved = !showSaved || savedIds.has(p.id);
		return matchTopic && matchSearch && matchSaved;
	});

	// ── Admin CRUD ─────────────────────────────────────────────────────────────

	function startAdd() {
		addingNew = true;
		editingId = null;
		confirmDeleteId = null;
		formTitle = '';
		formText = '';
		formTopic = selectedTopic !== 'All' && selectedTopic !== '__new__' ? selectedTopic : topics[1];
		newTopicName = '';
	}

	function startEdit(p: Prompt) {
		editingId = p.id;
		addingNew = false;
		confirmDeleteId = null;
		formTitle = p.title;
		formText = p.text;
		formTopic = p.topic;
	}

	function cancelForm() {
		editingId = null;
		addingNew = false;
		confirmDeleteId = null;
		newTopicName = '';
	}

	function saveEdit() {
		if (!formTitle.trim() || !formText.trim()) return;
		let topic = formTopic;
		if (formTopic === '__new__') {
			if (!newTopicName.trim()) return;
			topic = newTopicName.trim();
			if (!topics.includes(topic)) { topics = [...topics, topic]; saveCustomTopics(topics); }
		}
		prompts = prompts.map((p) =>
			p.id === editingId ? { ...p, title: formTitle.trim(), text: formText.trim(), topic } : p
		);
		savePrompts(prompts);
		toast.success('Prompt updated');
		cancelForm();
	}

	function saveNew() {
		if (!formTitle.trim() || !formText.trim()) return;
		let topic = formTopic;
		if (formTopic === '__new__') {
			if (!newTopicName.trim()) return;
			topic = newTopicName.trim();
			if (!topics.includes(topic)) { topics = [...topics, topic]; saveCustomTopics(topics); }
		}
		const newPrompt: Prompt = {
			id: `custom_${Date.now()}`,
			title: formTitle.trim(),
			text: formText.trim(),
			topic,
		};
		prompts = [...prompts, newPrompt];
		savePrompts(prompts);
		toast.success('Prompt added');
		cancelForm();
	}

	function deletePrompt(id: string) {
		prompts = prompts.filter((p) => p.id !== id);
		savePrompts(prompts);
		confirmDeleteId = null;
		toast.success('Prompt deleted');
	}

	// ── User actions ───────────────────────────────────────────────────────────

	function usePrompt(p: Prompt) {
		if (adminMode) return;
		omaPromptInsert.set(p.text);
		close();
	}

	function copyPrompt(p: Prompt) {
		navigator.clipboard.writeText(p.text).then(() => {
			toast.success('Prompt copied to clipboard');
		});
	}

	function toggleSaved(p: Prompt, e: MouseEvent) {
		e.stopPropagation();
		const next = new Set(savedIds);
		if (next.has(p.id)) next.delete(p.id); else next.add(p.id);
		savedIds = next;
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('oma_saved_prompts', JSON.stringify([...next]));
		}
	}

	// ── Modal control ──────────────────────────────────────────────────────────

	function close() {
		showOmaPromptLibrary.set(false);
		searchQuery = '';
		selectedTopic = 'All';
		showSaved = false;
		adminMode = false;
		cancelForm();
	}

	function handleBackdrop(e: MouseEvent) {
		if (e.target === e.currentTarget) close();
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			if (editingId || addingNew) { cancelForm(); return; }
			close();
		}
	}
</script>

<svelte:window on:keydown={onKeydown} />

{#if $showOmaPromptLibrary}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
		transition:fade={{ duration: 150 }}
		on:click={handleBackdrop}
		on:keydown={(e) => { if (e.key === 'Escape') close(); }}
		role="dialog"
		tabindex="-1"
		aria-modal="true"
		aria-label="Prompt Library"
	>
		<!-- Modal card -->
		<div class="relative flex w-full max-w-4xl h-[82vh] max-h-[700px] rounded-2xl bg-white dark:bg-gray-900 shadow-2xl overflow-hidden">

			<!-- ── Left sidebar ─────────────────────────────────────────────── -->
			<div class="flex flex-col w-60 shrink-0 border-r border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-950">

				<!-- Saved toggle -->
				<div class="px-4 pt-5 pb-3">
					<button
						on:click={() => { showSaved = !showSaved; selectedTopic = 'All'; adminMode = false; cancelForm(); }}
						class="w-full text-left text-sm font-medium px-3 py-2 rounded-lg transition
							{showSaved && !adminMode
								? 'bg-[#003877] text-white dark:bg-[#73B2F2]/20 dark:text-[#73B2F2]'
								: 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800'}"
					>
						Your saved prompts
					</button>
				</div>

				<!-- Topic list -->
				<div class="px-4 pb-3 flex-1 overflow-y-auto">
					<p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Prompt topics</p>
					<nav class="flex flex-col gap-0.5">
						{#each topics as topic}
							<button
								on:click={() => { selectedTopic = topic; showSaved = false; cancelForm(); }}
								class="w-full text-left text-sm px-3 py-1.5 rounded-lg transition
									{selectedTopic === topic && !showSaved && !adminMode
										? 'bg-[#003877] text-white dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] font-medium'
										: 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800'}"
							>
								{topic}
							</button>
						{/each}
					</nav>
				</div>

				<!-- Admin manage button -->
				{#if isAdmin}
					<div class="px-4 pb-3 border-t border-gray-100 dark:border-gray-800 pt-3">
						<button
							on:click={() => { adminMode = !adminMode; showSaved = false; selectedTopic = 'All'; searchQuery = ''; cancelForm(); }}
							class="w-full text-left text-sm px-3 py-2 rounded-lg transition font-medium
								{adminMode
									? 'bg-[#003877] text-white hover:bg-[#002a63] dark:bg-[#73B2F2]/20 dark:text-[#73B2F2]'
									: 'text-[#003877] dark:text-[#73B2F2] hover:bg-[#003877]/10 dark:hover:bg-[#73B2F2]/10 border border-[#003877]/30 dark:border-[#73B2F2]/30'}"
						>
							{adminMode ? '✓ Managing prompts' : 'Manage prompts'}
						</button>
					</div>
				{/if}

				<!-- Search -->
				<div class="px-4 pb-5">
					<div class="flex items-center gap-2 rounded-full border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2">
						<svg class="size-3.5 shrink-0 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
						</svg>
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="Find by keyword"
							class="w-full bg-transparent text-xs text-gray-700 dark:text-gray-300 placeholder-gray-400 outline-none"
						/>
					</div>
				</div>
			</div>

			<!-- ── Right panel ──────────────────────────────────────────────── -->
			<div class="flex flex-col flex-1 min-w-0">

				<!-- Header -->
				<div class="flex items-center justify-between px-6 pt-5 pb-3 shrink-0 border-b border-gray-100 dark:border-gray-800">
					<div class="flex items-center gap-3">
						<h2 class="text-base font-semibold text-gray-900 dark:text-gray-100">
							{adminMode ? 'Manage Prompts' : 'Prompt Library'}
						</h2>
						{#if adminMode}
							<span class="text-xs bg-[#003877]/10 dark:bg-[#73B2F2]/10 text-[#003877] dark:text-[#73B2F2] px-2 py-0.5 rounded-full font-medium">Admin</span>
						{/if}
					</div>
					<div class="flex items-center gap-2">
						{#if adminMode}
							<button
								on:click={startAdd}
								disabled={addingNew}
								class="flex items-center gap-1.5 text-xs font-medium bg-[#003877] text-white hover:bg-[#002a63] dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] dark:hover:bg-[#73B2F2]/30 px-3 py-1.5 rounded-full transition disabled:opacity-40"
							>
								<svg class="size-3.5" viewBox="0 0 20 20" fill="currentColor">
									<path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
								</svg>
								Add prompt
							</button>
						{/if}
						<button
							on:click={close}
							class="rounded-full p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
							aria-label="Close"
						>
							<svg class="size-5" viewBox="0 0 20 20" fill="currentColor">
								<path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
							</svg>
						</button>
					</div>
				</div>

				<!-- Active filter chips (user mode only) -->
				{#if !adminMode && (selectedTopic !== 'All' || showSaved || searchQuery)}
					<div class="px-6 pt-2 pb-1 flex items-center gap-2 shrink-0">
						<svg class="size-3.5 text-gray-400 shrink-0" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M2.628 1.601C5.028 1.206 7.49 1 10 1s4.973.206 7.372.601a.75.75 0 01.628.74v2.288a2.25 2.25 0 01-.659 1.59l-4.682 4.683a2.25 2.25 0 00-.659 1.59v3.037c0 .684-.31 1.33-.844 1.757l-1.937 1.55A.75.75 0 018 18.25v-5.757a2.25 2.25 0 00-.659-1.591L2.659 6.22A2.25 2.25 0 012 4.629V2.34a.75.75 0 01.628-.74z" clip-rule="evenodd" />
						</svg>
						{#if showSaved}<span class="text-xs rounded-full bg-[#003877] text-white dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] px-3 py-0.5 font-medium">Saved</span>{/if}
						{#if selectedTopic !== 'All'}<span class="text-xs rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-3 py-0.5">{selectedTopic}</span>{/if}
						{#if searchQuery}<span class="text-xs rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-3 py-0.5">"{searchQuery}"</span>{/if}
						<button on:click={() => { selectedTopic = 'All'; showSaved = false; searchQuery = ''; }} class="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">Clear</button>
					</div>
				{/if}

				<!-- Prompt list -->
				<div class="flex-1 overflow-y-auto px-6 pb-6">

					<!-- New prompt form -->
					{#if addingNew}
						<div class="mt-4 mb-2 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 p-4" transition:slide={{ duration: 150 }}>
							<p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">New prompt</p>
							<div class="flex flex-col gap-3">
								<div class="flex gap-3">
									<div class="flex-1">
										<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Title</label>
										<input
											type="text"
											bind:value={formTitle}
											placeholder="Short label"
											class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]"
										/>
									</div>
									<div>
										<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Topic</label>
										<div class="flex flex-col gap-1">
											<select
												bind:value={formTopic}
												class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]"
											>
												{#each topics.slice(1) as t}
													<option value={t}>{t}</option>
												{/each}
												<option value="__new__">+ Add new topic…</option>
											</select>
											{#if formTopic === '__new__'}
												<input
													type="text"
													bind:value={newTopicName}
													placeholder="New topic name"
													class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]"
												/>
											{/if}
										</div>
									</div>
								</div>
								<div>
									<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Prompt text</label>
									<textarea
										bind:value={formText}
										placeholder="Write the prompt… use [placeholders] for variable parts."
										rows="3"
										class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2] resize-none"
									/>
								</div>
								<div class="flex gap-2 justify-end">
									<button on:click={cancelForm} class="text-sm px-4 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition">Cancel</button>
									<button on:click={saveNew} disabled={!formTitle.trim() || !formText.trim() || (formTopic === '__new__' && !newTopicName.trim())} class="text-sm px-4 py-1.5 rounded-full bg-[#003877] text-white hover:bg-[#002a63] dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] dark:hover:bg-[#73B2F2]/30 transition disabled:opacity-40">Save</button>
								</div>
							</div>
						</div>
					{/if}

					<!-- Prompt cards -->
					{#if filtered.length === 0 && !addingNew}
						<p class="text-sm text-gray-400 dark:text-gray-500 mt-8 text-center">No prompts found.</p>
					{:else}
						{#each filtered as prompt (prompt.id)}
							<div class="group border-b border-gray-100 dark:border-gray-800 py-4 last:border-0">

								<!-- Edit form inline -->
								{#if editingId === prompt.id}
									<div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4" transition:slide={{ duration: 120 }}>
										<p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">Edit prompt</p>
										<div class="flex flex-col gap-3">
											<div class="flex gap-3">
												<div class="flex-1">
													<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Title</label>
													<input type="text" bind:value={formTitle} class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]" />
												</div>
												<div>
													<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Topic</label>
													<div class="flex flex-col gap-1">
														<select bind:value={formTopic} class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]">
															{#each topics.slice(1) as t}
																<option value={t}>{t}</option>
															{/each}
															<option value="__new__">+ Add new topic…</option>
														</select>
														{#if formTopic === '__new__'}
															<input
																type="text"
																bind:value={newTopicName}
																placeholder="New topic name"
																class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2]"
															/>
														{/if}
													</div>
												</div>
											</div>
											<div>
												<label class="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Prompt text</label>
												<textarea bind:value={formText} rows="3" class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-[#003877] dark:focus:ring-[#73B2F2] resize-none" />
											</div>
											<div class="flex gap-2 justify-end">
												<button on:click={cancelForm} class="text-sm px-4 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition">Cancel</button>
												<button on:click={saveEdit} disabled={!formTitle.trim() || !formText.trim() || (formTopic === '__new__' && !newTopicName.trim())} class="text-sm px-4 py-1.5 rounded-full bg-[#003877] text-white hover:bg-[#002a63] dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] dark:hover:bg-[#73B2F2]/30 transition disabled:opacity-40">Save</button>
											</div>
										</div>
									</div>

								<!-- Delete confirmation inline -->
								{:else if confirmDeleteId === prompt.id}
									<div class="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 p-4" transition:slide={{ duration: 120 }}>
										<p class="text-sm font-medium text-red-700 dark:text-red-400 mb-1">Delete "{prompt.title}"?</p>
										<p class="text-xs text-red-500 dark:text-red-500 mb-3">This cannot be undone.</p>
										<div class="flex gap-2">
											<button on:click={() => confirmDeleteId = null} class="text-sm px-4 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition">Cancel</button>
											<button on:click={() => deletePrompt(prompt.id)} class="text-sm px-4 py-1.5 rounded-full bg-red-600 text-white hover:bg-red-700 transition">Delete</button>
										</div>
									</div>

								<!-- Normal prompt card -->
								{:else}
									<div class="flex items-start justify-between gap-3">
										<div class="flex-1 min-w-0">
											<div class="flex items-center gap-2 mb-1">
												<p class="text-xs font-semibold text-gray-500 dark:text-gray-400">{prompt.title}</p>
												{#if adminMode}
													<span class="text-[10px] bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 px-1.5 py-px rounded">{prompt.topic}</span>
												{/if}
											</div>
											<button
												on:click={() => usePrompt(prompt)}
												class="text-left text-sm font-medium text-gray-900 dark:text-gray-100 leading-snug
													{!adminMode ? 'hover:text-[#003877] dark:hover:text-[#73B2F2] transition cursor-pointer' : 'cursor-default'}"
											>
												{prompt.text}
											</button>
											{#if !adminMode}
												<div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition">
													<button
														on:click={() => copyPrompt(prompt)}
														class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-[#003877] dark:hover:text-[#73B2F2] transition"
													>
														<svg class="size-3" viewBox="0 0 16 16" fill="currentColor">
															<path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
														</svg>
														Copy
													</button>
													<span class="text-gray-200 dark:text-gray-700">|</span>
													<button
														on:click={() => usePrompt(prompt)}
														class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-[#003877] dark:hover:text-[#73B2F2] transition"
													>
														<svg class="size-3" viewBox="0 0 20 20" fill="currentColor">
															<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
														</svg>
														Use this prompt
													</button>
												</div>
											{/if}
										</div>

										<!-- Right icons: bookmark (user) or edit+delete (admin) -->
										{#if adminMode}
											<div class="flex items-center gap-1 shrink-0 mt-0.5">
												<button
													on:click={() => startEdit(prompt)}
													class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
													aria-label="Edit"
												>
													<svg class="size-4" viewBox="0 0 20 20" fill="currentColor">
														<path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" /><path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
													</svg>
												</button>
												<button
													on:click={() => { confirmDeleteId = prompt.id; editingId = null; addingNew = false; }}
													class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition"
													aria-label="Delete"
												>
													<svg class="size-4" viewBox="0 0 20 20" fill="currentColor">
														<path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
													</svg>
												</button>
											</div>
										{:else}
											<button
												on:click={(e) => toggleSaved(prompt, e)}
												class="shrink-0 mt-0.5 p-1 rounded transition
												{savedIds.has(prompt.id)
													? 'text-[#003877] dark:text-[#73B2F2]'
													: 'text-gray-300 dark:text-gray-600 hover:text-[#003877] dark:hover:text-[#73B2F2]'}"
												aria-label={savedIds.has(prompt.id) ? 'Remove from saved' : 'Save prompt'}
											>
												<Bookmark className="size-4" filled={savedIds.has(prompt.id)} />
											</button>
										{/if}
									</div>
								{/if}
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
