<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { updateFolderById } from '$lib/apis/folders';

	import {
		config,
		user,
		models as _models,
		temporaryChatEnabled,
		selectedFolder
	} from '$lib/stores';
	import { refreshChatList } from '$lib/stores/chatList';
	import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

	import Suggestions from './Suggestions.svelte';
	import OmaSuggestions from './OmaSuggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';
	import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
	import FolderTitle from './Placeholder/FolderTitle.svelte';
	import { goto } from '$app/navigation';
	import { showOmaFeedback } from '$lib/stores/omaFeedback';
	import { showOmaHelp } from '$lib/stores/omaHelp';
	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import ChatBubbleOval from '$lib/components/icons/ChatBubbleOval.svelte';
	import QuestionMarkCircle from '$lib/components/icons/QuestionMarkCircle.svelte';

	const i18n = getContext('i18n');

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];
	export let messageInput = null;

	export let selectedToolIds = [];
	export let selectedSkillIds = [];
	export let selectedFilterIds = [];
	export let pendingOAuthTools = [];

	export let showCommands = false;

	export let imageGenerationEnabled = false;
	export let codeInterpreterEnabled = false;
	export let webSearchEnabled = false;

	export let onUpload: Function = (e) => {};
	export let onSelect = (e) => {};
	export let onChange = (e) => {};
	export let onWebSearchToggle: Function = () => {};

	export let toolServers = [];

	export let dragged = false;

	let models = [];
	let selectedModelIdx = 0;

	$: if (selectedModels.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));

	// True when viewing a shared folder the current user doesn't own AND lacks write access
	$: folderReadOnly =
		$selectedFolder != null &&
		$selectedFolder.user_id !== $user?.id &&
		$selectedFolder.permission !== 'write';
</script>

<div class="flex flex-col h-full w-full max-w-[58rem] mx-auto px-2 @2xl:px-20">
<div class="flex-1 flex flex-col items-center justify-center text-center translate-y-6 py-16">
	{#if $temporaryChatEnabled}
		<Tooltip
			content={$i18n.t("This chat won't appear in history and your messages will not be saved.")}
			className="w-full flex justify-center mb-0.5"
			placement="top"
		>
			<div class="flex items-center gap-1.5 text-gray-500 text-xs my-1 w-fit">
				<EyeSlash strokeWidth="2" className="size-3.5" />{$i18n.t('Temporary Chat')}
			</div>
		</Tooltip>
	{/if}

	<div class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4">
		<div class="w-full flex flex-col justify-center items-center">
			{#if $selectedFolder}
				<FolderTitle
					folder={$selectedFolder}
					readOnly={folderReadOnly}
					onUpdate={async (folder) => {
						await refreshChatList(localStorage.token);
					}}
					onDelete={async () => {
						await refreshChatList(localStorage.token);

						selectedFolder.set(null);
					}}
				/>
			{:else}
				<div class="flex flex-row justify-center gap-2.5 @sm:gap-3 w-fit px-5 max-w-xl">
					<div class="flex shrink-0 justify-center">
						<div class="flex -space-x-4 mb-0.5" in:fade={{ duration: 100 }}>
							{#each models as model, modelIdx}
								<Tooltip
									content={(models[modelIdx]?.info?.meta?.tags ?? [])
										.map((tag) => tag.name.toUpperCase())
										.join(', ')}
									placement="top"
								>
									<button
										aria-hidden={models.length <= 1}
										aria-label={$i18n.t('Get information on {{name}} in the UI', {
											name: models[modelIdx]?.name
										})}
										on:click={() => {
											selectedModelIdx = modelIdx;
										}}
									>
										<img
											src={`${WEBUI_API_BASE_URL}/models/model/profile/image?id=${model?.id}&lang=${$i18n.language}`}
											class=" size-9 @sm:size-10 rounded-2xl"
											aria-hidden="true"
											draggable="false"
											on:error={(e) => {
												e.currentTarget.src = '/favicon.png';
											}}
										/>
									</button>
								</Tooltip>
							{/each}
						</div>
					</div>

					<div
						class=" text-2xl @sm:text-2xl line-clamp-1 flex items-center"
						in:fade={{ duration: 100 }}
					>
						{#if models[selectedModelIdx]?.name}
							<Tooltip
								content={models[selectedModelIdx]?.name}
								placement="top"
								className=" flex items-center "
							>
								<span class="line-clamp-1">
									{models[selectedModelIdx]?.name}
								</span>
							</Tooltip>
						{:else}
							{$i18n.t('Hello, {{name}}', { name: $user?.name })}
						{/if}
					</div>
				</div>

				<div class="flex mt-1 mb-2">
					<div in:fade={{ duration: 100, delay: 50 }}>
						{#if models[selectedModelIdx]?.info?.meta?.description ?? null}
							<Tooltip
								className=" w-fit"
								content={DOMPurify.sanitize(
									marked.parse(
										sanitizeResponseContent(
											models[selectedModelIdx]?.info?.meta?.description ?? ''
										).replaceAll('\n', '<br>')
									)
								)}
								placement="top"
							>
								<div
									class="mt-0.5 px-2 text-sm font-normal text-gray-500 dark:text-gray-400 line-clamp-2 max-w-xl markdown"
								>
									{@html DOMPurify.sanitize(
										marked.parse(
											sanitizeResponseContent(
												models[selectedModelIdx]?.info?.meta?.description ?? ''
											).replaceAll('\n', '<br>')
										)
									)}
								</div>
							</Tooltip>

							{#if models[selectedModelIdx]?.info?.meta?.user}
								<div class="mt-0.5 text-sm font-normal text-gray-400 dark:text-gray-500">
									By
									{#if models[selectedModelIdx]?.info?.meta?.user.community}
										<a
											href="https://openwebui.com/m/{models[selectedModelIdx]?.info?.meta?.user
												.username}"
											>{models[selectedModelIdx]?.info?.meta?.user.name
												? models[selectedModelIdx]?.info?.meta?.user.name
												: `@${models[selectedModelIdx]?.info?.meta?.user.username}`}</a
										>
									{:else}
										{models[selectedModelIdx]?.info?.meta?.user.name}
									{/if}
								</div>
							{/if}
						{/if}
					</div>
				</div>
			{/if}

			<div class="text-base font-normal @md:max-w-3xl w-full py-3 {atSelectedModel ? 'mt-2' : ''}">
				{#if !($selectedFolder && folderReadOnly)}
					<MessageInput
						bind:this={messageInput}
						{history}
						bind:selectedModels
						bind:files
						bind:prompt
						bind:autoScroll
						bind:selectedToolIds
						bind:selectedSkillIds
						bind:selectedFilterIds
						bind:imageGenerationEnabled
						bind:codeInterpreterEnabled
						bind:webSearchEnabled
						bind:atSelectedModel
						bind:showCommands
						bind:dragged
						{pendingOAuthTools}
						{toolServers}
						{stopResponse}
						{createMessagePair}
						placeholder={$i18n.t('How can I help you today?')}
						{onChange}
						{onUpload}
						{onWebSearchToggle}
						on:chatVariables
						on:submit={(e) => {
							dispatch('submit', e.detail);
						}}
					/>
				{/if}
			</div>
		</div>
	</div>

	{#if $selectedFolder}
		<div class="mx-auto px-4 md:max-w-3xl md:px-6 min-h-62" in:fade={{ duration: 200, delay: 200 }}>
			<FolderPlaceholder folder={$selectedFolder} />
		</div>
	{:else}
		<div class="max-w-lg w-full mx-auto mt-2" in:fade={{ duration: 200, delay: 200 }}>
			<!-- OMA: generic suggestions replaced with O&M quick-start prompts -->
			<OmaSuggestions on:select={(e) => onSelect(e.detail)} />
			<!-- OMA: disabled generic Suggestions
			<Suggestions
				suggestionPrompts={atSelectedModel?.info?.meta?.suggestion_prompts ??
					models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
					$config?.default_prompt_suggestions ??
					[]}
				inputValue={prompt}
				{onSelect}
			/>
			-->
		</div>
	{/if}

</div>

<!-- OMA: quick-access pills — bottom of home page, aligned to content column -->
{#if !$selectedFolder}
	<!-- OMA: Enerparc brand glow blob — sibling of pills, absolute within column -->
	<div class="oma-home-glow pointer-events-none"></div>
	<div class="relative pb-5 flex items-center justify-center gap-2 z-10">
		<button
			type="button"
			on:click={() => goto('/workspace/prompts')}
			class="flex items-center gap-1.5 rounded-full border border-white/40 bg-white/20 px-3.5 py-1.5 text-xs text-gray-600 backdrop-blur-sm transition hover:bg-white/35 hover:text-gray-800 dark:border-white/15 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20 dark:hover:text-gray-100"
		>
			<BookOpen className="size-3.5" strokeWidth="1.75" />
			{$i18n.t('Prompt Library')}
		</button>
		<button
			type="button"
			on:click={() => showOmaFeedback.set(true)}
			class="flex items-center gap-1.5 rounded-full border border-white/40 bg-white/20 px-3.5 py-1.5 text-xs text-gray-600 backdrop-blur-sm transition hover:bg-white/35 hover:text-gray-800 dark:border-white/15 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20 dark:hover:text-gray-100"
		>
			<ChatBubbleOval className="size-3.5" strokeWidth="1.75" />
			{$i18n.t('Feedback')}
		</button>
		<button
			type="button"
			on:click={() => showOmaHelp.set(true)}
			class="flex items-center gap-1.5 rounded-full border border-white/40 bg-white/20 px-3.5 py-1.5 text-xs text-gray-600 backdrop-blur-sm transition hover:bg-white/35 hover:text-gray-800 dark:border-white/15 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20 dark:hover:text-gray-100"
		>
			<QuestionMarkCircle className="size-3.5" strokeWidth="1.75" />
			{$i18n.t('Help')}
		</button>
	</div>
{/if}


</div>

<style>
	.oma-home-glow {
		position: fixed;
		left: 0;
		width: 100vw;
		height: 300px;
		bottom: -90px;
		background: radial-gradient(ellipse at calc(50% + 128px) 60%, rgba(0, 40, 100, 1) 0%, rgba(0, 70, 170, 0.95) 18%, rgba(0, 90, 200, 0.88) 32%, rgba(115, 178, 242, 0.65) 50%, rgba(173, 210, 248, 0.25) 65%, transparent 78%);
		filter: blur(110px);
		border-radius: 50%;
		z-index: 0;
		animation: oma-glow-breathe 5s ease-in-out infinite;
		transform-origin: center center;
	}
	@keyframes oma-glow-breathe {
		0%, 100% {
			transform: scale(1) scaleX(1);
			border-radius: 50%;
			opacity: 1;
		}
		40% {
			transform: scale(1.08) scaleX(1.12);
			border-radius: 55% 45% 52% 48% / 50% 55% 45% 50%;
			opacity: 0.82;
		}
		70% {
			transform: scale(0.82) scaleX(0.88);
			border-radius: 45% 55% 48% 52% / 52% 45% 55% 48%;
			opacity: 0.6;
		}
	}
	.oma-home-glow::after {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: 50%;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");
		background-size: 180px 180px;
		opacity: 0.22;
		mix-blend-mode: overlay;
	}
	:global(.dark) .oma-home-glow {
		background: radial-gradient(ellipse at calc(50% + 128px) 65%, rgba(115, 178, 242, 0.85) 0%, rgba(0, 100, 200, 0.5) 40%, rgba(0, 56, 119, 0.2) 60%, transparent 78%);
	}
	:global(.dark) .oma-home-glow::after {
		opacity: 0.18;
	}
</style>
