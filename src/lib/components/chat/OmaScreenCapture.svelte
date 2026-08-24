<!-- ---------------------------------------------------------------------------
  File:        OmaScreenCapture.svelte
  Description: Screen-area capture tool. Uses getDisplayMedia to capture the
               screen, then lets the user drag to select a region. Emits the
               cropped image as a data-URL via the 'capture' event.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { getContext } from 'svelte';

	const i18n: any = getContext('i18n');
	const dispatch = createEventDispatcher<{ capture: string; cancel: void }>();

	// ── State ─────────────────────────────────────────────────────────────────
	let capturing = false;
	let error = '';

	// Overlay drag state
	let overlayCanvas: HTMLCanvasElement;
	let videoEl: HTMLVideoElement;
	let stream: MediaStream | null = null;

	let dragStart: { x: number; y: number } | null = null;
	let dragEnd: { x: number; y: number } | null = null;
	let isDragging = false;

	// ── Start capture flow ────────────────────────────────────────────────────
	async function startCapture() {
		error = '';
		try {
			stream = await navigator.mediaDevices.getDisplayMedia({
				video: { mediaSource: 'screen' } as any,
				audio: false
			});
		} catch {
			error = $i18n.t('Screen capture was cancelled or denied.');
			return;
		}
		capturing = true;
		// Let the overlay render, then hook the video
		setTimeout(initOverlay, 50);
	}

	function initOverlay() {
		if (!videoEl || !stream) return;
		videoEl.srcObject = stream;
		videoEl.onloadedmetadata = () => {
			videoEl.play();
			drawFrame();
		};
	}

	// ── Draw live frame onto canvas ───────────────────────────────────────────
	let animFrame: number;
	function drawFrame() {
		if (!overlayCanvas || !videoEl) return;
		const ctx = overlayCanvas.getContext('2d')!;
		overlayCanvas.width = window.innerWidth;
		overlayCanvas.height = window.innerHeight;
		ctx.drawImage(videoEl, 0, 0, overlayCanvas.width, overlayCanvas.height);
		drawSelectionRect(ctx);
		animFrame = requestAnimationFrame(drawFrame);
	}

	function drawSelectionRect(ctx: CanvasRenderingContext2D) {
		if (!dragStart || !dragEnd) return;
		const x = Math.min(dragStart.x, dragEnd.x);
		const y = Math.min(dragStart.y, dragEnd.y);
		const w = Math.abs(dragEnd.x - dragStart.x);
		const h = Math.abs(dragEnd.y - dragStart.y);

		// Dim everything outside selection
		ctx.fillStyle = 'rgba(0,0,0,0.45)';
		ctx.fillRect(0, 0, overlayCanvas.width, overlayCanvas.height);

		// Clear inside selection (show live screen)
		ctx.clearRect(x, y, w, h);
		ctx.drawImage(videoEl, x, y, w, h, x, y, w, h);

		// Selection border
		ctx.strokeStyle = '#3b82f6';
		ctx.lineWidth = 2;
		ctx.strokeRect(x, y, w, h);
	}

	// ── Mouse events ──────────────────────────────────────────────────────────
	function onMouseDown(e: MouseEvent) {
		dragStart = { x: e.clientX, y: e.clientY };
		dragEnd = { x: e.clientX, y: e.clientY };
		isDragging = true;
	}

	function onMouseMove(e: MouseEvent) {
		if (!isDragging) return;
		dragEnd = { x: e.clientX, y: e.clientY };
	}

	function onMouseUp() {
		if (!isDragging || !dragStart || !dragEnd) return;
		isDragging = false;
		cropAndFinish();
	}

	// ── Crop selection and emit ───────────────────────────────────────────────
	function cropAndFinish() {
		if (!dragStart || !dragEnd || !overlayCanvas || !videoEl) return;

		cancelAnimationFrame(animFrame);

		const x = Math.min(dragStart.x, dragEnd.x);
		const y = Math.min(dragStart.y, dragEnd.y);
		const w = Math.abs(dragEnd.x - dragStart.x);
		const h = Math.abs(dragEnd.y - dragStart.y);

		if (w < 10 || h < 10) {
			cancel();
			return;
		}

		// Draw the raw screen frame (no dim overlay) onto a crop canvas
		const cropCanvas = document.createElement('canvas');
		cropCanvas.width = w;
		cropCanvas.height = h;
		const ctx = cropCanvas.getContext('2d')!;

		// Scale from display coords to video resolution
		const scaleX = videoEl.videoWidth / window.innerWidth;
		const scaleY = videoEl.videoHeight / window.innerHeight;
		ctx.drawImage(
			videoEl,
			x * scaleX, y * scaleY, w * scaleX, h * scaleY,
			0, 0, w, h
		);

		const dataUrl = cropCanvas.toDataURL('image/png');
		stopStream();
		capturing = false;
		dispatch('capture', dataUrl);
	}

	// ── Cancel / cleanup ──────────────────────────────────────────────────────
	function cancel() {
		cancelAnimationFrame(animFrame);
		stopStream();
		capturing = false;
		dragStart = null;
		dragEnd = null;
		dispatch('cancel');
	}

	function stopStream() {
		stream?.getTracks().forEach((t) => t.stop());
		stream = null;
	}

	onDestroy(() => {
		cancelAnimationFrame(animFrame);
		stopStream();
	});
</script>

<!-- Trigger button -->
{#if !capturing}
	<button
		type="button"
		on:click={startCapture}
		class="flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-xs text-gray-600 transition hover:border-[#003877] hover:text-[#003877] dark:border-white/10 dark:bg-white/5 dark:text-gray-400 dark:hover:border-[#73B2F2] dark:hover:text-[#73B2F2]"
	>
		<!-- camera icon -->
		<svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
			<path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
			<path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
		</svg>
		{$i18n.t('Capture screenshot')}
	</button>
	{#if error}
		<p class="mt-1 text-xs text-red-500">{error}</p>
	{/if}
{/if}

<!-- Fullscreen capture overlay -->
{#if capturing}
	<!-- Hidden video to hold the stream -->
	<video bind:this={videoEl} class="hidden" muted playsinline></video>

	<!-- Canvas overlay — fullscreen, on top of everything -->
	<div
		class="fixed inset-0 z-[9999] cursor-crosshair select-none"
		on:mousedown={onMouseDown}
		on:mousemove={onMouseMove}
		on:mouseup={onMouseUp}
		role="presentation"
	>
		<canvas bind:this={overlayCanvas} class="h-full w-full"></canvas>

		<!-- Instruction bar -->
		<div class="pointer-events-none absolute left-1/2 top-4 -translate-x-1/2 rounded-full bg-black/70 px-4 py-2 text-xs text-white backdrop-blur-sm">
			{$i18n.t('Drag to select an area')} &nbsp;·&nbsp;
			<button
				class="pointer-events-auto underline"
				on:click={cancel}
				type="button"
			>{$i18n.t('Cancel')}</button>
		</div>
	</div>
{/if}
