<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext, onDestroy, onMount, tick } from 'svelte';
	const i18n = getContext('i18n');

	import Modal from '$lib/components/common/Modal.svelte';
	import SearchInput from './Sidebar/SearchInput.svelte';
	import {
		getChatById,
		getChatList,
		getChatListBySearchText,
		cloneChatById,
		deleteChatById,
		archiveChatById,
		updateChatById,
		updateChatFolderIdById,
		getAllTags
	} from '$lib/apis/chats';
	import Spinner from '../common/Spinner.svelte';

	import dayjs from '$lib/dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import calendar from 'dayjs/plugin/calendar';
	import Loader from '../common/Loader.svelte';
	import { createMessagesList } from '$lib/utils';
	import { getOutputText } from '$lib/components/chat/Messages/structuredOutput';
	import { config, user, chatId as currentChatId, tags } from '$lib/stores';
	import { refreshChatList } from '$lib/stores/chatList';
	import Messages from '../chat/Messages.svelte';
	import { goto } from '$app/navigation';
	import EditPencilIcon from './Sidebar/icons/EditPencil.svelte';
	import NotesIcon from './Sidebar/icons/Notes.svelte';

	import ChatMenu from './Sidebar/ChatMenu.svelte';
	import ShareChatModal from '../chat/ShareChatModal.svelte';
	import DeleteConfirmDialog from '../common/ConfirmDialog.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import Sparkles from '../icons/Sparkles.svelte';
	import ArchiveBox from '../icons/ArchiveBox.svelte';
	import GarbageBin from '../icons/GarbageBin.svelte';
	import { generateTitle } from '$lib/apis';
	import { artifacts, loadImageBlob, type ArtifactItem } from '$lib/stores/artifacts';
	dayjs.extend(calendar);
	dayjs.extend(localizedFormat);

	export let show = false;
	export let onClose = () => {};

	// OMA: tab state for search filter
	let activeTab: 'chats' | 'images' | 'files' = 'chats';
	let selectedArtifact: ArtifactItem | null = null;
	let artifactImageSrc: string | null = null;

	$: filteredArtifacts = $artifacts
		.filter((a) => (activeTab === 'images' ? a.type === 'image' : a.type === 'document'))
		.filter((a) => !query.trim() || a.name.toLowerCase().includes(query.toLowerCase().trim()));

	$: if (selectedArtifact?.type === 'image') {
		loadImageBlob(selectedArtifact.id).then((src) => { artifactImageSrc = src; });
	} else {
		artifactImageSrc = null;
	}

	const downloadArtifact = async (artifact: ArtifactItem) => {
		if (artifact.type === 'document' && artifact.url) {
			const a = document.createElement('a');
			a.href = artifact.url;
			a.download = artifact.name;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		} else if (artifact.type === 'image') {
			const src = await loadImageBlob(artifact.id);
			if (src) {
				const a = document.createElement('a');
				a.href = src;
				a.download = artifact.name;
				document.body.appendChild(a);
				a.click();
				document.body.removeChild(a);
			}
		}
	};

	let showShareChatModal = false;
	let showDeleteConfirm = false;
	let menuChatId = '';
	let menuChatTitle = '';

	let editingChatId = null;
	let editingChatTitle = '';

	let shiftKey = false;

	const onShiftKeyDown = (e) => {
		if (e.key === 'Shift') shiftKey = true;
	};

	const onShiftKeyUp = (e) => {
		if (e.key === 'Shift') shiftKey = false;
	};
	let generating = false;

	const refreshSidebar = async () => {
		await refreshChatList(localStorage.token, { refreshPinned: true });
	};

	const cloneChatHandler = async (id) => {
		const chat = chatList?.find((c) => c.id === id);
		const res = await cloneChatById(
			localStorage.token,
			id,
			$i18n.t('Clone of {{TITLE}}', {
				TITLE: chat?.title ?? 'Chat'
			})
		).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			await refreshSidebar();
			await searchHandler();
		}
	};

	const archiveChatHandler = async (id) => {
		try {
			await archiveChatById(localStorage.token, id);

			chatList = chatList?.filter((c) => c.id !== id) ?? null;

			if ($currentChatId === id) {
				await goto('/');
				currentChatId.set('');
			}

			await refreshSidebar();
			toast.success($i18n.t('Chat archived.'));
		} catch (error) {
			toast.error($i18n.t('Failed to archive chat.'));
		}
	};

	const deleteChatHandler = async (id) => {
		const res = await deleteChatById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			chatList = chatList?.filter((c) => c.id !== id) ?? null;
			tags.set(await getAllTags(localStorage.token));

			if ($currentChatId === id) {
				await goto('/');
				currentChatId.set('');
			}

			await refreshSidebar();
		}
	};

	const moveChatHandler = async (chatId, folderId) => {
		if (chatId && folderId) {
			const res = await updateChatFolderIdById(localStorage.token, chatId, folderId).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				chatList = chatList?.filter((c) => c.id !== chatId) ?? null;
				await refreshSidebar();
				toast.success($i18n.t('Chat moved successfully'));
			}
		}
	};

	const renameHandler = async (id) => {
		editingChatId = id;
		editingChatTitle = chatList?.find((c) => c.id === id)?.title ?? '';

		await tick();
		const input = document.getElementById(`search-chat-title-input-${id}`);
		if (input) {
			input.focus();
			input.select();
		}
	};

	const confirmRename = async () => {
		if (!editingChatId) return;

		const trimmed = editingChatTitle.trim();
		if (trimmed === '') {
			toast.error($i18n.t('Title cannot be an empty string.'));
			return;
		}

		await updateChatById(localStorage.token, editingChatId, { title: trimmed });

		if (chatList) {
			chatList = chatList.map((c) => (c.id === editingChatId ? { ...c, title: trimmed } : c));
		}

		editingChatId = null;
		editingChatTitle = '';
		await refreshSidebar();
	};

	const cancelRename = () => {
		editingChatId = null;
		editingChatTitle = '';
	};

	const generateTitleHandler = async () => {
		if (!editingChatId || generating) return;

		generating = true;
		const chat = await getChatById(localStorage.token, editingChatId).catch(() => null);

		if (!chat) {
			toast.error($i18n.t('Failed to load chat'));
			generating = false;
			return;
		}

		const chatContent = chat.chat;
		const history = chatContent?.history;
		let msgList = [];

		if (history?.messages && history?.currentId) {
			msgList = createMessagesList(history, history.currentId).map((m: any) => ({
				role: m.role,
				content: getOutputText(m.output) || m.content || ''
			}));
		} else {
			msgList = (chatContent?.messages ?? []).map((m: any) => ({
				role: m.role,
				content: getOutputText(m.output) || m.content || ''
			}));
		}

		let model = '';
		if (history?.messages && history?.currentId) {
			let currentId = history.currentId;
			while (currentId) {
				const msg = history.messages[currentId];
				if (!msg) break;
				if (msg.role === 'assistant' && msg.model) {
					model = msg.model;
					break;
				}
				currentId = msg.parentId;
			}
		}
		if (!model) {
			model = chatContent?.models?.at(0) ?? '';
		}

		editingChatTitle = '';

		const generatedTitle = await generateTitle(localStorage.token, model, msgList).catch(
			(error) => {
				toast.error(`${error}`);
				return null;
			}
		);

		if (generatedTitle) {
			editingChatTitle = generatedTitle;
		}

		generating = false;

		if (generatedTitle) {
			await confirmRename();
		}
	};

	let actions = [
		{
			label: $i18n.t('Start a new conversation'),
			onClick: async () => {
				await goto(`/${query ? `?q=${query}` : ''}`);
				show = false;
				onClose();
			},
			icon: EditPencilIcon
		}
	];

	let query = '';
	let page = 1;

	let chatList = null;

	let chatListLoading = false;
	let allChatsLoaded = false;

	let searchDebounceTimeout;

	let selectedIdx = null;
	let selectedChat = null;

	let selectedModels = [''];
	let history = null;
	let messages = null;
	let messagesContainerElement: HTMLElement | null = null;
	const messagesContainerId = 'chat-preview';

	const searchFilterPrefixes = ['tag:', 'folder:', 'pinned:', 'archived:', 'shared:'];

	const getSnippetQuery = (query: string) => {
		return query
			.trim()
			.split(/\s+/)
			.filter(
				(word) => !searchFilterPrefixes.some((prefix) => word.toLowerCase().startsWith(prefix))
			)
			.join(' ')
			.trim();
	};

	const getHighlightedSnippet = (snippet: string, query: string) => {
		const match = getSnippetQuery(query).toLowerCase();
		const matchIndex = match ? snippet.toLowerCase().indexOf(match) : -1;

		if (matchIndex === -1) {
			return [{ text: snippet, highlight: false }];
		}

		const start = Math.max(matchIndex - 60, 0);
		const end = Math.min(matchIndex + match.length + 80, snippet.length);
		const visibleSnippet = `${start > 0 ? '...' : ''}${snippet.slice(start, end)}${
			end < snippet.length ? '...' : ''
		}`;
		const index = visibleSnippet.toLowerCase().indexOf(match);

		return [
			{ text: visibleSnippet.slice(0, index), highlight: false },
			{ text: visibleSnippet.slice(index, index + match.length), highlight: true },
			{ text: visibleSnippet.slice(index + match.length), highlight: false }
		].filter((part) => part.text);
	};

	$: if (!chatListLoading && chatList) {
		loadChatPreview(selectedIdx);
	}

	const scrollPreviewToBottom = async () => {
		await tick();
		requestAnimationFrame(() => {
			if (messagesContainerElement) {
				messagesContainerElement.scrollTop = messagesContainerElement.scrollHeight;

				requestAnimationFrame(() => {
					if (messagesContainerElement) {
						messagesContainerElement.scrollTop = messagesContainerElement.scrollHeight;
					}
				});
			}
		});
		setTimeout(() => {
			if (messagesContainerElement) {
				messagesContainerElement.scrollTop = messagesContainerElement.scrollHeight;
			}
		}, 80);
	};

	const loadChatPreview = async (selectedIdx) => {
		if (!chatList || chatList.length === 0 || selectedIdx === null) {
			selectedChat = null;
			messages = null;
			history = null;
			selectedModels = [''];
			return;
		}

		const selectedChatIdx = selectedIdx - actions.length;
		if (selectedChatIdx < 0 || selectedChatIdx >= chatList.length) {
			selectedChat = null;
			messages = null;
			history = null;
			selectedModels = [''];
			return;
		}

		const chatId = chatList[selectedChatIdx].id;

		const chat = await getChatById(localStorage.token, chatId).catch(async (error) => {
			return null;
		});

		if (chat) {
			selectedChat = chat;

			if (chat?.chat?.history) {
				selectedModels =
					(chat?.chat?.models ?? undefined) !== undefined
						? chat?.chat?.models
						: [chat?.chat?.models ?? ''];

				history = chat?.chat?.history;
				messages = [];
				await scrollPreviewToBottom();
			} else {
				messages = [];
			}
		} else {
			toast.error($i18n.t('Failed to load chat preview'));
			selectedChat = null;
			messages = null;
			history = null;
			selectedModels = [''];
			return;
		}
	};

	const searchHandler = async () => {
		if (!show) {
			return;
		}

		if (searchDebounceTimeout) {
			clearTimeout(searchDebounceTimeout);
		}

		page = 1;
		chatList = null;
		if (query === '') {
			chatList = await getChatList(localStorage.token, page);
		} else {
			searchDebounceTimeout = setTimeout(async () => {
				chatList = await getChatListBySearchText(localStorage.token, query, page);

				if ((chatList ?? []).length === 0) {
					allChatsLoaded = true;
				} else {
					allChatsLoaded = false;
				}
			}, 500);
		}

		selectedChat = null;
		messages = null;
		history = null;
		selectedModels = [''];

		if ((chatList ?? []).length === 0) {
			allChatsLoaded = true;
		} else {
			allChatsLoaded = false;
		}
	};

	const loadMoreChats = async () => {
		chatListLoading = true;
		page += 1;

		let newChatList = [];

		if (query) {
			newChatList = await getChatListBySearchText(localStorage.token, query, page);
		} else {
			newChatList = await getChatList(localStorage.token, page);
		}

		// once the bottom of the list has been reached (no results) there is no need to continue querying
		allChatsLoaded = newChatList.length === 0;

		if (newChatList.length > 0) {
			const existingIds = new Set(chatList.map((c) => c.id));
			const uniqueNewChats = newChatList.filter((c) => !existingIds.has(c.id));
			chatList = [...chatList, ...uniqueNewChats];
		}

		chatListLoading = false;
	};

	$: if (show) {
		searchHandler();
	} else {
		editingChatId = null;
		editingChatTitle = '';
		generating = false;
	}

	const onKeyDown = (e) => {
		// Ignore keydown fired while confirming an IME composition (e.g. Japanese/Chinese/Korean)
		// so confirming the composition with Enter doesn't trigger search actions (#26172).
		if (e.isComposing || e.keyCode === 229) {
			return;
		}

		const searchOptions = document.getElementById('search-options-container');
		if (searchOptions || !show) {
			return;
		}

		// Don't handle navigation/activation keys while editing a chat title
		if (editingChatId) {
			return;
		}

		if (e.code === 'Escape') {
			show = false;
			onClose();
		} else if (e.code === 'Enter') {
			const item = document.querySelector(`[data-arrow-selected="true"]`);
			if (item) {
				item?.click();
				show = false;
			}

			return;
		} else if (e.code === 'ArrowDown') {
			const searchInput = document.getElementById('search-input');

			if (searchInput) {
				// check if focused on the search input
				if (document.activeElement === searchInput) {
					searchInput.blur();
					selectedIdx = 0;
					return;
				}
			}

			selectedIdx = Math.min(selectedIdx + 1, (chatList ?? []).length - 1 + actions.length);
		} else if (e.code === 'ArrowUp') {
			if (selectedIdx === 0) {
				const searchInput = document.getElementById('search-input');

				if (searchInput) {
					// check if focused on the search input
					if (document.activeElement !== searchInput) {
						searchInput.focus();
						selectedIdx = 0;
						return;
					}
				}
			}

			selectedIdx = Math.max(selectedIdx - 1, 0);
		}

		const item = document.querySelector(`[data-arrow-selected="true"]`);
		item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
	};

	onMount(() => {
		actions = [
			...actions,
			...(($config?.features?.enable_notes ?? false) &&
			($user?.role === 'admin' || ($user?.permissions?.features?.notes ?? true))
				? [
						{
							label: $i18n.t('Create a new note'),
							onClick: async () => {
								await goto(`/notes?content=${query}`);
								show = false;
								onClose();
							},
							icon: NotesIcon
						}
					]
				: [])
		];

		document.addEventListener('keydown', onKeyDown);
		document.addEventListener('keydown', onShiftKeyDown);
		document.addEventListener('keyup', onShiftKeyUp);
	});

	onDestroy(() => {
		if (searchDebounceTimeout) {
			clearTimeout(searchDebounceTimeout);
		}
		document.removeEventListener('keydown', onKeyDown);
		document.removeEventListener('keydown', onShiftKeyDown);
		document.removeEventListener('keyup', onShiftKeyUp);
	});
</script>

<ShareChatModal bind:show={showShareChatModal} chatId={menuChatId} />

<DeleteConfirmDialog
	bind:show={showDeleteConfirm}
	title={$i18n.t('Delete chat?')}
	on:confirm={() => {
		deleteChatHandler(menuChatId);
	}}
>
	<div class="text-sm text-gray-500 flex-1 line-clamp-3">
		{$i18n.t('This will delete')} <span class="font-normal">{menuChatTitle}</span>.
	</div>
</DeleteConfirmDialog>

<Modal size="xl" bind:show>
	<div class="py-2.5 dark:text-gray-300 text-gray-700">
		<div class="px-3.5 pb-1">
			<SearchInput
				bind:value={query}
				on:input={searchHandler}
				placeholder={$i18n.t('Search')}
				showClearButton={true}
				onFocus={() => {
					selectedIdx = null;
					messages = null;
				}}
				onKeydown={(e) => {
					if (e.code === 'Enter' && (chatList ?? []).length > 0) {
						const item = document.querySelector(`[data-arrow-selected="true"]`);
						if (item) {
							item?.click();
						}

						show = false;
						return;
					} else if (e.code === 'ArrowDown') {
						selectedIdx = Math.min(selectedIdx + 1, (chatList ?? []).length - 1 + actions.length);
					} else if (e.code === 'ArrowUp') {
						selectedIdx = Math.max(selectedIdx - 1, 0);
					} else {
						selectedIdx = 0;
					}

					const item = document.querySelector(`[data-arrow-selected="true"]`);
					item?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
				}}
			/>
		</div>

		<!-- OMA: filter tabs — Chats / Artifact Images / Artifact Files -->
		<div class="flex gap-1.5 px-3.5 pb-2 pt-1">
			{#each [
				{ id: 'chats', label: $i18n.t('Chats') },
				{ id: 'images', label: $i18n.t('Images') },
				{ id: 'files', label: $i18n.t('Files') }
			] as tab}
				<button
					class="px-3 py-1 rounded-full text-xs font-medium transition-colors
						{activeTab === tab.id
							? 'bg-[#003877] text-white'
							: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}"
					on:click={() => {
						activeTab = tab.id;
						selectedArtifact = null;
						selectedChat = null;
						messages = null;
					}}
				>
					{tab.label}
				</button>
			{/each}
		</div>

		<div class="flex px-3.5 pb-0.5">
			<div
				class="flex flex-col overflow-y-auto h-96 md:h-[40rem] max-h-full scrollbar-hidden w-full flex-1 pr-2"
			>
				<!-- OMA: disabled — Actions section (Start new conversation / Create note) not needed for O&M users -->

				{#if activeTab === 'chats'}
				{#if chatList}
					<div aria-hidden="true" class="h-px my-3"></div>

					{#if chatList.length === 0}
						<div class="text-xs text-gray-500 dark:text-gray-400 text-center px-5 py-4">
							{$i18n.t('No results found')}
						</div>
					{/if}

					{#each chatList as chat, idx (chat.id)}
						{#if idx === 0 || (idx > 0 && chat.time_range !== chatList[idx - 1].time_range)}
							<div
								class="w-full text-xs text-gray-500 dark:text-gray-500 font-normal {idx === 0
									? ''
									: 'pt-4'} pb-1.5 px-2"
							>
								{$i18n.t(chat.time_range)}
								<!-- localisation keys for time_range to be recognized from the i18next parser (so they don't get automatically removed):
							{$i18n.t('Today')}
							{$i18n.t('Yesterday')}
							{$i18n.t('Previous 7 days')}
							{$i18n.t('Previous 30 days')}
							{$i18n.t('January')}
							{$i18n.t('February')}
							{$i18n.t('March')}
							{$i18n.t('April')}
							{$i18n.t('May')}
							{$i18n.t('June')}
							{$i18n.t('July')}
							{$i18n.t('August')}
							{$i18n.t('September')}
							{$i18n.t('October')}
							{$i18n.t('November')}
							{$i18n.t('December')}
							-->
							</div>
						{/if}

						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div
							class="w-full flex justify-between items-center rounded-lg text-sm py-1.5 pl-2.5 pr-32 hover:bg-gray-50/70 dark:hover:bg-gray-850/50 group/item relative {selectedIdx ===
							idx + actions.length
								? 'bg-gray-50/70 dark:bg-gray-850/50'
								: ''}"
							data-arrow-selected={selectedIdx === idx + actions.length ? 'true' : undefined}
							on:mouseenter={() => {
								selectedIdx = idx + actions.length;
							}}
						>
							{#if editingChatId === chat.id}
								<div class="flex-1 min-w-0">
									<input
										id="search-chat-title-input-{chat.id}"
										bind:value={editingChatTitle}
										class="bg-transparent w-full outline-none"
										placeholder={generating ? $i18n.t('Generating...') : ''}
										disabled={generating}
										on:keydown={(e) => {
											e.stopPropagation();
											if (e.key === 'Enter') {
												e.preventDefault();
												confirmRename();
											} else if (e.key === 'Escape') {
												e.preventDefault();
												cancelRename();
											}
										}}
										on:blur={() => {
											if (!generating) {
												confirmRename();
											}
										}}
									/>
								</div>

								<div class="flex items-center shrink-0 pl-1">
									<Tooltip content={$i18n.t('Generate')}>
										<button
											class="self-center dark:hover:text-white transition disabled:cursor-not-allowed"
											disabled={generating}
											on:mousedown|preventDefault={() => {}}
											on:click|preventDefault|stopPropagation={() => {
												generateTitleHandler();
											}}
										>
											{#if generating}
												<Spinner className="size-4" />
											{:else}
												<Sparkles strokeWidth="2" />
											{/if}
										</button>
									</Tooltip>
								</div>
							{:else}
								<a
									class="flex-1 min-w-0"
									href="/c/{chat.id}"
									draggable="false"
									on:click={async () => {
										await goto(`/c/${chat.id}`);
										show = false;
										onClose();
									}}
								>
									<div class="text-ellipsis line-clamp-1 w-full">
										{chat?.title}
									</div>
									{#if chat?.snippet}
										<div class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mt-0.5">
											{#each getHighlightedSnippet(chat.snippet, query) as part}
												{#if part.highlight}
													<mark
														class="rounded bg-yellow-200/70 px-0.5 text-inherit dark:bg-yellow-500/30"
													>
														{part.text}
													</mark>
												{:else}
													{part.text}
												{/if}
											{/each}
										</div>
									{/if}
								</a>
							{/if}

							<div
								class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-3 pl-6 shrink-0"
							>
								<div class="text-gray-500 dark:text-gray-400 text-xs">
									{$i18n.t(
										dayjs(chat?.updated_at * 1000).calendar(null, {
											sameDay: '[Today]',
											nextDay: '[Tomorrow]',
											nextWeek: 'dddd',
											lastDay: '[Yesterday]',
											lastWeek: '[Last] dddd',
											sameElse: 'L'
										})
									)}
								</div>

								{#if editingChatId !== chat.id}
									{#if shiftKey}
										<div class="flex items-center space-x-1.5">
											<Tooltip content={$i18n.t('Archive')} className="flex items-center">
												<button
													class="self-center dark:hover:text-white transition"
													on:click|stopPropagation={() => {
														archiveChatHandler(chat.id);
													}}
													type="button"
												>
													<ArchiveBox className="size-4 translate-y-[0.5px]" strokeWidth="2" />
												</button>
											</Tooltip>

											<Tooltip content={$i18n.t('Delete')}>
												<button
													class="self-center dark:hover:text-white transition"
													on:click|stopPropagation={() => {
														deleteChatHandler(chat.id);
													}}
													type="button"
												>
													<GarbageBin strokeWidth="2" />
												</button>
											</Tooltip>
										</div>
									{:else}
										<div class="flex items-center">
											<ChatMenu
												chatId={chat.id}
												shareHandler={() => {
													menuChatId = chat.id;
													showShareChatModal = true;
												}}
												{moveChatHandler}
												cloneChatHandler={() => {
													cloneChatHandler(chat.id);
												}}
												archiveChatHandler={() => {
													archiveChatHandler(chat.id);
												}}
												renameHandler={() => {
													renameHandler(chat.id);
												}}
												deleteHandler={() => {
													menuChatId = chat.id;
													menuChatTitle = chat.title;
													showDeleteConfirm = true;
												}}
												onClose={() => {}}
												onPinChange={async () => {
													await refreshSidebar();
													await searchHandler();
												}}
											>
												<button
													aria-label="Chat Menu"
													class="self-center dark:hover:text-white transition"
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 16 16"
														fill="currentColor"
														class="w-4 h-4"
													>
														<path
															d="M2 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM6.5 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM12.5 6.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z"
														/>
													</svg>
												</button>
											</ChatMenu>
										</div>
									{/if}
								{/if}
							</div>
						</div>
					{/each}

					{#if !allChatsLoaded}
						<Loader
							on:visible={(e) => {
								if (!chatListLoading) {
									loadMoreChats();
								}
							}}
						>
							<div class="w-full flex justify-center py-4 text-xs animate-pulse items-center gap-2">
								<Spinner className=" size-4" />
								<div class=" ">{$i18n.t('Loading...')}</div>
							</div>
						</Loader>
					{/if}
				{:else}
					<div class="w-full h-full flex justify-center items-center">
						<Spinner className="size-5" />
					</div>
				{/if}
				<!-- end chats tab -->
				{:else}
				<!-- OMA: artifact results (images / files) -->
				{#if filteredArtifacts.length === 0}
					<div class="text-xs text-gray-500 dark:text-gray-400 text-center px-5 py-4">
						{$i18n.t('No results found')}
					</div>
				{:else}
					<div class="w-full text-xs text-gray-500 dark:text-gray-500 font-normal pb-2 px-2">
						{activeTab === 'images' ? $i18n.t('Images') : $i18n.t('Files')}
					</div>
					{#each filteredArtifacts as artifact (artifact.id)}
						<button
							class="w-full flex items-center gap-3 rounded-lg text-sm py-2 px-2.5 text-left
								hover:bg-gray-50/70 dark:hover:bg-gray-850/50
								{selectedArtifact?.id === artifact.id ? 'bg-gray-50/70 dark:bg-gray-850/50' : ''}"
							on:click={() => { selectedArtifact = artifact; }}
						>
							<!-- icon -->
							<div class="shrink-0 text-gray-400 dark:text-gray-500">
								{#if artifact.type === 'image'}
									<svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
										<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 9.75h.008v.008H3V9.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM6.375 6h11.25A2.625 2.625 0 0120.25 8.625v6.75A2.625 2.625 0 0117.625 18H6.375A2.625 2.625 0 013.75 15.375v-6.75A2.625 2.625 0 016.375 6z" />
									</svg>
								{:else if artifact.ext === 'pdf'}
									<svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
										<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
									</svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
										<path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75.125V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M5.625 4.5h12.75a1.125 1.125 0 011.125 1.125v9c0 .621-.504 1.125-1.125 1.125H5.625a1.125 1.125 0 01-1.125-1.125v-9A1.125 1.125 0 015.625 4.5z" />
									</svg>
								{/if}
							</div>
							<div class="flex-1 min-w-0">
								<div class="text-ellipsis line-clamp-1 text-gray-800 dark:text-gray-200">
									{artifact.name}
								</div>
								<div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
									{dayjs(artifact.ts).format('ll')}
								</div>
							</div>
						</button>
					{/each}
				{/if}
				{/if}
			</div>

			<!-- Right panel: chat preview (chats tab) OR artifact detail (image/file tabs) -->
			{#if activeTab === 'chats'}
			<div
				id={messagesContainerId}
				bind:this={messagesContainerElement}
				class="hidden md:flex md:flex-1 w-full overflow-y-auto h-96 md:h-[40rem] scrollbar-hidden @container"
			>
				{#if messages === null}
					<div
						class="w-full h-full flex justify-center items-center text-gray-500 dark:text-gray-400 text-sm"
					>
						{$i18n.t('Select a conversation to preview')}
					</div>
				{:else}
					<div class="w-full h-full flex flex-col">
						<Messages
							className="h-full flex pt-4 pb-8 w-full"
							chatId={`chat-preview-${selectedChat?.id ?? ''}`}
							user={$user}
							readOnly={true}
							{selectedModels}
							bind:history
							autoScroll={true}
							{messagesContainerId}
							messagesCount={8}
							sendMessage={() => {}}
							continueResponse={() => {}}
							regenerateResponse={() => {}}
						/>
					</div>
				{/if}
			</div>
			{:else}
			<!-- OMA: artifact detail panel -->
			<div class="hidden md:flex md:flex-1 w-full overflow-y-auto h-96 md:h-[40rem] scrollbar-hidden">
				{#if selectedArtifact === null}
					<div class="w-full h-full flex justify-center items-center text-gray-500 dark:text-gray-400 text-sm">
						{$i18n.t('Select a file to preview')}
					</div>
				{:else}
					<div class="w-full p-5 flex flex-col gap-4">
						<!-- image thumbnail -->
						{#if selectedArtifact.type === 'image' && artifactImageSrc}
							<img
								src={artifactImageSrc}
								alt={selectedArtifact.name}
								class="w-full max-h-52 object-contain rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900"
							/>
						{/if}
						<!-- file info -->
						<div class="flex flex-col gap-3">
							<div class="font-medium text-sm text-gray-800 dark:text-gray-200 break-all">
								{selectedArtifact.name}
							</div>
							<div class="flex items-center gap-2 flex-wrap">
								<span class="px-2 py-0.5 rounded text-xs font-semibold uppercase bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
									{selectedArtifact.type === 'image' ? 'Image' : (selectedArtifact.ext?.toUpperCase() ?? 'File')}
								</span>
								<span class="text-xs text-gray-500 dark:text-gray-400">
									{dayjs(selectedArtifact.ts).format('LL')}
								</span>
							</div>
							<button
								class="mt-1 w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
									bg-[#003877] hover:bg-[#002a63] text-white text-sm font-medium transition-colors"
								on:click={() => downloadArtifact(selectedArtifact)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
								</svg>
								{$i18n.t('Download')}
							</button>
						</div>
					</div>
				{/if}
			</div>
			{/if}
		</div>
	</div>
</Modal>
