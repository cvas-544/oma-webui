<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, onDestroy, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import { getBackendConfig } from '$lib/apis';
	import { getSessionUser, userSignIn, updateUserTimezone } from '$lib/apis/auths';

	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';
	import { getUserTimezone } from '$lib/utils';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let dropdownOpen = false;

	const bgImages = [
		'/oma-login-bg-01.png',
		'/oma-login-bg-02.png',
		'/oma-login-bg-03.png'
	];
	let currentBg = 0;
	let bgInterval: ReturnType<typeof setInterval>;

	const tools = [
		{ id: 'oma', name: 'O&M Assistant', desc: 'O&M AI for PV plants' }
	];

	let selectedTool = tools[0];

	const setSessionUser = async (sessionUser, redirectPath: string | null = null) => {
		if (sessionUser) {
			console.log(sessionUser);
			toast.success($i18n.t(`You're now logged in.`));
			if (sessionUser.token) {
				localStorage.token = sessionUser.token;
			}
			$socket.emit('user-join', { auth: { token: sessionUser.token } });
			await user.set(sessionUser);
			await config.set(await getBackendConfig());

			const timezone = getUserTimezone();
			if (sessionUser.token && timezone) {
				updateUserTimezone(sessionUser.token, timezone);
			}

			if (!redirectPath) {
				redirectPath = $page.url.searchParams.get('redirect') || '/';
			}

			goto(redirectPath);
			localStorage.removeItem('redirectPath');
		}
	};

	const signInHandler = async () => {
		const sessionUser = await userSignIn('', '').catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		await setSessionUser(sessionUser);
	};

	const oauthCallbackHandler = async () => {
		function getCookie(name) {
			const match = document.cookie.match(
				new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)')
			);
			return match ? decodeURIComponent(match[1]) : null;
		}

		const token = getCookie('token');
		if (!token) {
			return;
		}

		const sessionUser = await getSessionUser(token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (!sessionUser) {
			return;
		}

		localStorage.token = token;
		await setSessionUser(sessionUser, localStorage.getItem('redirectPath') || null);
	};

	function selectTool(tool) {
		selectedTool = tool;
		dropdownOpen = false;
		try {
			localStorage.setItem('oma_selected_tool', tool.id);
		} catch (e) {}
	}

	function handleMicrosoftLogin() {
		localStorage.setItem('oma_selected_tool', selectedTool.id);
		window.location.href = `${WEBUI_BASE_URL}/oauth/microsoft/login`;
	}

	function handleClickOutside(e) {
		const el = document.getElementById('tool-selector');
		if (el && !el.contains(e.target)) {
			dropdownOpen = false;
		}
	}

	onMount(async () => {
		const redirectPath = $page.url.searchParams.get('redirect');
		if ($user) {
			goto(redirectPath || '/');
		} else {
			if (redirectPath) {
				localStorage.setItem('redirectPath', redirectPath);
			}
		}

		const error = $page.url.searchParams.get('error');
		if (error) {
			toast.error(error);
		}

		await oauthCallbackHandler();

		const saved = localStorage.getItem('oma_selected_tool');
		if (saved) {
			const found = tools.find((t) => t.id === saved);
			if (found) selectedTool = found;
		}

		loaded = true;

		bgInterval = setInterval(() => {
			currentBg = (currentBg + 1) % bgImages.length;
		}, 10000);

		if (($config?.features?.auth_trusted_header ?? false) || $config?.features?.auth === false) {
			await signInHandler();
		}
	});

	onDestroy(() => {
		if (bgInterval) clearInterval(bgInterval);
	});
</script>

<svelte:head>
	<title>{`${$WEBUI_NAME}`}</title>
</svelte:head>

<svelte:window on:click={handleClickOutside} />

<div class="oma-login-viewport" id="auth-page">
	<!-- Background carousel -->
	{#each bgImages as src, i}
		<div class="oma-bg-layer" class:active={currentBg === i}>
			<img {src} alt="" class="oma-bg-img" />
		</div>
	{/each}
	<div class="oma-bg-overlay" />

	<div class="w-full absolute top-0 left-0 right-0 h-8 drag-region" />

	{#if loaded}
		{#if ($config?.features.auth_trusted_header ?? false) || $config?.features.auth === false}
			<div class="oma-login-card">
				<div class="flex items-center justify-center gap-3 text-xl">
					<span>{$i18n.t('Signing in...')}</span>
					<Spinner className="size-5" />
				</div>
			</div>
		{:else}
			<div class="oma-login-card" id="auth-login-card">
				<!-- Logo -->
				<div class="flex flex-col items-center mb-10">
					<img
						src="/enerparc-full-logo.png"
						alt="Enerparc"
						class="h-10 mb-3"
					/>
					<div class="text-xs text-gray-500 tracking-widest uppercase">AI Tools Platform</div>
				</div>

				<!-- Tool selector -->
				<div class="flex flex-col">
					<label class="text-sm font-normal text-left mb-1.5 block text-gray-700 dark:text-gray-300" for="tool-selector-btn">Select your AI tool</label>
					<div class="oma-tool-selector relative" id="tool-selector" class:open={dropdownOpen}>
						<button
							class="flex items-center gap-3 w-full my-0.5 text-sm outline-hidden bg-gray-700/5 dark:bg-gray-100/5 rounded-xl px-3.5 py-2.5 transition hover:bg-gray-700/10 dark:hover:bg-gray-100/10"
							id="tool-selector-btn"
							type="button"
							aria-expanded={dropdownOpen}
							aria-haspopup="listbox"
							on:click|stopPropagation={() => (dropdownOpen = !dropdownOpen)}
						>
							<div class="flex-1 text-left">
								<div class="text-sm font-normal text-gray-900 dark:text-gray-100">{selectedTool.name}</div>
								<div class="text-xs text-gray-500 dark:text-gray-400">{selectedTool.desc}</div>
							</div>
							<svg class="w-4 h-4 text-gray-400 transition-transform" class:rotate-180={dropdownOpen} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<polyline points="6 9 12 15 18 9" />
							</svg>
						</button>

						{#if dropdownOpen}
							<div class="absolute top-full left-0 right-0 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl mt-1 shadow-lg z-10 overflow-hidden" role="listbox">
								{#each tools as tool}
									<button
										class="flex items-center gap-3 w-full px-3.5 py-2.5 text-left transition"
										class:bg-gray-100={selectedTool.id === tool.id}
										class:dark:bg-gray-800={selectedTool.id === tool.id}
										class:hover:bg-gray-50={selectedTool.id !== tool.id}
										class:dark:hover:bg-gray-800={selectedTool.id !== tool.id}
										role="option"
										aria-selected={selectedTool.id === tool.id}
										on:click|stopPropagation={() => selectTool(tool)}
									>
										<div class="flex-1">
											<div class="text-sm font-normal text-gray-900 dark:text-gray-100">{tool.name}</div>
											<div class="text-xs text-gray-500 dark:text-gray-400">{tool.desc}</div>
										</div>
										{#if selectedTool.id === tool.id}
											<svg class="w-4 h-4 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
												<polyline points="20 6 9 17 4 12" />
											</svg>
										{/if}
									</button>
								{/each}
							</div>
						{/if}
					</div>
				</div>

				<div class="my-6 border-t border-gray-200 dark:border-gray-700"></div>

				<!-- Microsoft button -->
				<div class="mt-0 flex justify-center">
					<button
						class="oma-ms-btn flex justify-center items-center transition rounded-full font-medium text-sm py-4 text-white px-10"
						type="button"
						on:click={handleMicrosoftLogin}
					>
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="size-5 mr-3" aria-hidden="true">
							<path d="M16.555 3.843l3.602 3.602a2.877 2.877 0 0 1 0 4.069l-2.643 2.643a2.877 2.877 0 0 1-4.069 0l-.301-.301l-6.558 6.558a2 2 0 0 1-1.239.578L5.172 20.999H4a1 1 0 0 1-.993-.883L3 20v-1.172a2 2 0 0 1 .467-1.284l.119-.13L10.143 10.857l-.301-.301a2.877 2.877 0 0 1 0-4.069l2.643-2.643a2.877 2.877 0 0 1 4.069 0z" />
							<path d="M14.5 7.5l2 2" />
						</svg>
						<span>Continue with Microsoft</span>
					</button>
				</div>

				<div class="mt-4 text-center text-xs text-gray-400">
					Secured by Azure AD &middot; Enerparc AG
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.oma-login-viewport {
		width: 100%;
		height: 100vh;
		height: 100dvh;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		overflow: hidden;
	}

	.oma-bg-layer {
		position: absolute;
		inset: 0;
		z-index: 0;
		opacity: 0;
		transition: opacity 1.5s ease-in-out;
	}

	.oma-bg-layer.active {
		opacity: 1;
	}

	.oma-bg-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.oma-bg-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(
			160deg,
			rgba(12, 35, 64, 0.35) 0%,
			rgba(12, 35, 64, 0.15) 50%,
			rgba(12, 35, 64, 0.3) 100%
		);
		z-index: 1;
	}

	.oma-login-card {
		position: relative;
		z-index: 2;
		background: #ffffff;
		border-radius: 20px;
		padding: 64px 44px;
		width: 448px;
		max-width: calc(100% - 40px);
		box-shadow:
			0 4px 6px rgba(0, 0, 0, 0.04),
			0 20px 50px rgba(12, 35, 64, 0.18);
	}

	.oma-ms-btn {
		background-color: #143773;
	}

	.oma-ms-btn:hover {
		background-color: #1a4590;
	}

	@media (max-width: 480px) {
		.oma-login-card {
			padding: 32px 24px;
			border-radius: 16px;
		}
	}
</style>
