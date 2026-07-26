<script lang="ts">
	import { onDestroy, getContext } from 'svelte';

	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import XMark from '$lib/components/icons/XMark.svelte';

	export let show = false;
	export let src = '';
	export let alt = '';

	const i18n = getContext('i18n');

	let previewElement = null;

	const handleKeyDown = (event: KeyboardEvent) => {
		if (event.key === 'Escape') {
			show = false;
		}
	};

	$: if (show && previewElement) {
		document.body.appendChild(previewElement);
		window.addEventListener('keydown', handleKeyDown);
		document.body.style.overflow = 'hidden';
	} else if (previewElement) {
		window.removeEventListener('keydown', handleKeyDown);
		document.body.removeChild(previewElement);
		document.body.style.overflow = 'unset';
	}

	onDestroy(() => {
		window.removeEventListener('keydown', handleKeyDown);
		show = false;
		if (previewElement && previewElement.parentNode === document.body) {
			document.body.removeChild(previewElement);
		}
		document.body.style.overflow = 'unset';
	});

	const downloadImage = async () => {
		const fileName = (alt || 'chart') + '.png';
		if (src.startsWith('data:image/')) {
			const base64Data = src.split(',')[1];
			const blob = new Blob([Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0))], {
				type: 'image/png'
			});
			saveAs(blob, fileName);
			return;
		}
		try {
			const res = await fetch(src);
			const blob = await res.blob();
			saveAs(blob, fileName);
		} catch {
			// CORS fallback: anchor click — server sends attachment disposition so browser downloads
			const a = document.createElement('a');
			a.href = src;
			a.download = fileName;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		}
	};
</script>

{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		bind:this={previewElement}
		class="modal fixed top-0 right-0 left-0 bottom-0 bg-black/20 w-full min-h-screen h-screen flex justify-center items-center z-9999 overflow-hidden overscroll-contain"
		on:click={(e) => { if (e.target === e.currentTarget) show = false; }}
	>
		<div class="relative flex flex-col items-center" style="max-width: 65vw; max-height: 65vh;">
			<!-- Controls -->
			<div class="absolute -top-9 left-0 right-0 flex justify-between items-center px-1">
				<button
					class="text-white bg-black/50 hover:bg-black/70 rounded-full p-1 transition"
					on:pointerdown={(e) => { e.stopImmediatePropagation(); e.preventDefault(); show = false; }}
					on:click={() => { show = false; }}
					aria-label={$i18n.t('Close')}
				>
					<XMark className={'size-4'} />
				</button>

				<button
					class="text-white bg-black/50 hover:bg-black/70 rounded-full p-1 transition"
					on:click={downloadImage}
					aria-label={$i18n.t('Download')}
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
						<path d="M10.75 2.75a.75.75 0 0 0-1.5 0v8.614L6.295 8.235a.75.75 0 1 0-1.09 1.03l4.25 4.5a.75.75 0 0 0 1.09 0l4.25-4.5a.75.75 0 0 0-1.09-1.03l-2.955 3.129V2.75Z" />
						<path d="M3.5 12.75a.75.75 0 0 0-1.5 0v2.5A2.75 2.75 0 0 0 4.75 18h10.5A2.75 2.75 0 0 0 18 15.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5Z" />
					</svg>
				</button>
			</div>

			<img
				{src}
				{alt}
				class="rounded-lg object-contain select-none shadow-2xl"
				style="max-width: 65vw; max-height: 65vh;"
				draggable="false"
			/>
		</div>
	</div>
{/if}
