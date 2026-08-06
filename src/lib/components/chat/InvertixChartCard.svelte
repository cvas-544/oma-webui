<script lang="ts">
	// ---------------------------------------------------------------------------
	// File:        InvertixChartCard.svelte
	// Description: Renders Chart.js charts inline in the message bubble via a
	//              sandboxed iframe. Driven by invertix:chart events from the
	//              chart filter. Click opens the Artifacts panel for full
	//              interactive expand/zoom.
	// Author:      Vasu Chukka
	// Co-author:   Claude Code
	// ---------------------------------------------------------------------------

	import { showArtifacts, showControls, artifactContents } from '$lib/stores';
	import { tick } from 'svelte';

	export let charts: {
		type: string;
		title?: string;
		labels?: string[];
		datasets?: any[];
		options?: any;
		filename?: string;
	}[] = [];
	export let chartLibCode: string = '';

	function buildChartHtml(config: any): string {
		const canvasId = 'chart_' + Math.random().toString(36).slice(2, 8);
		const filename = config.filename || 'chart';

		const chartJsConfig = {
			type: config.type || 'bar',
			data: {
				labels: config.labels || [],
				datasets: (config.datasets || []).map((ds: any) => {
					const out = { ...ds };
					const pal = out.palette === 'financial' ? 'FIN_PALETTE' : 'CHART_PALETTE';
					delete out.palette;
					if (!out.backgroundColor) out.backgroundColor = pal;
					if (!out.borderColor) out.borderColor = pal + '[0]';
					if (!out.borderWidth) out.borderWidth = 1;
					return out;
				})
			},
			options: config.options || {
				responsive: true,
				plugins: {
					title: {
						display: !!config.title,
						text: config.title || '',
						color: 'CHART_TEXT_REF',
						font: { size: 16 }
					},
					legend: { labels: { color: 'CHART_TEXT_REF' } }
				},
				scales: {
					x: {
						ticks: { color: 'CHART_TEXT_REF' },
						grid: { color: 'CHART_GRID_REF' },
						title: { display: !!config.xLabel, text: config.xLabel || '', color: 'CHART_TEXT_REF' }
					},
					y: {
						ticks: { color: 'CHART_TEXT_REF' },
						grid: { color: 'CHART_GRID_REF' },
						title: { display: !!config.yLabel, text: config.yLabel || '', color: 'CHART_TEXT_REF' }
					}
				}
			}
		};

		let configStr = JSON.stringify(chartJsConfig);
		configStr = configStr.replace(/\"CHART_PALETTE\[0\]\"/g, 'CHART_PALETTE[0]');
		configStr = configStr.replace(/\"FIN_PALETTE\[0\]\"/g, 'FIN_PALETTE[0]');
		configStr = configStr.replace(/\"CHART_PALETTE\"/g, 'CHART_PALETTE');
		configStr = configStr.replace(/\"FIN_PALETTE\"/g, 'FIN_PALETTE');
		configStr = configStr.replace(/\"CHART_TEXT_REF\"/g, 'CHART_TEXT');
		configStr = configStr.replace(/\"CHART_GRID_REF\"/g, 'CHART_GRID');

		return `<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<style>
		body { margin: 0; background-color: #F6F7FB; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
		#chart-wrap { padding: 16px; border-radius: 8px; max-width: 720px; margin: auto; }
	</style>
</head>
<body>
	<div id="chart-wrap">
		<canvas id="${canvasId}"></canvas>
	</div>
	<script>
		${chartLibCode}
		document.body.style.backgroundColor = CHART_BG;
		var ctx = document.getElementById('${canvasId}').getContext('2d');
		new Chart(ctx, ${configStr});
		addDownloadButton('${canvasId}', '${filename.replace(/'/g, "\\'")}');
	</script>
</body>
</html>`;
	}

	async function expandChart(config: any) {
		const html = buildChartHtml(config);
		artifactContents.set([{ type: 'iframe', content: html }]);
		await tick();
		showArtifacts.set(true);
		showControls.set(true);
	}
</script>

{#if charts.length > 0}
	{#each charts as config, i}
		<div class="my-2 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
			on:click={() => expandChart(config)}
			on:keydown={(e) => e.key === 'Enter' && expandChart(config)}
			role="button"
			tabindex="0"
			title="Click to expand chart"
		>
			<iframe
				srcdoc={buildChartHtml(config)}
				sandbox="allow-scripts"
				style="width:100%;height:360px;border:none;pointer-events:none;"
				title={config.title || 'Chart'}
			></iframe>
			<div class="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-800 text-xs text-gray-500 dark:text-gray-400">
				<span>{config.title || 'Interactive chart'}</span>
				<span class="flex items-center gap-1">
					<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<polyline points="15 3 21 3 21 9" />
						<polyline points="9 21 3 21 3 15" />
						<line x1="21" y1="3" x2="14" y2="10" />
						<line x1="3" y1="21" x2="10" y2="14" />
					</svg>
					Expand
				</span>
			</div>
		</div>
	{/each}
{/if}
