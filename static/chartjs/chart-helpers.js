// ---------------------------------------------------------------------------
// Enerparc brand palette + PNG download helper.
// Injected alongside chart.umd.min.js into every chart iframe by Chat.svelte.
// Single source of truth — matches sandbox_executor.py preamble constants.
// ---------------------------------------------------------------------------

// Energy / O&M palette
const CHART_BG       = '#F6F7FB';
const CHART_AXES_BG  = '#EBF4FB';
const CHART_TEXT     = '#0C2742';
const CHART_MUTED    = '#3D6D88';
const CHART_GRID     = '#D0DFF0';
const CHART_PALETTE  = ['#65B5E2','#003877','#0C2742','#3D6D88','#73B2F2'];
const CHART_ACCENT   = '#65B5E2';

// Financial palette (same brand blues for now — diverge if needed)
const FIN_PALETTE    = ['#65B5E2','#003877','#0C2742','#3D6D88','#73B2F2'];

// Chart.js global defaults — apply Enerparc theme to every chart automatically
Chart.defaults.color = CHART_TEXT;
Chart.defaults.borderColor = CHART_GRID;
Chart.defaults.backgroundColor = CHART_PALETTE[0];
Chart.defaults.font.family = "'Inter', 'Segoe UI', system-ui, sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// PNG download helper — adds a "Save as PNG" button below every canvas
function addDownloadButton(canvasId, filename) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    var btn = document.createElement('button');
    btn.textContent = '⭳ Save as PNG';
    btn.style.cssText = 'margin:8px 0;padding:6px 14px;border:1px solid ' + CHART_GRID +
        ';border-radius:6px;background:white;color:' + CHART_TEXT +
        ';cursor:pointer;font-size:13px;font-family:inherit;';
    btn.onmouseover = function() { btn.style.background = CHART_AXES_BG; };
    btn.onmouseout  = function() { btn.style.background = 'white'; };
    btn.onclick = function() {
        var tmpCanvas = document.createElement('canvas');
        tmpCanvas.width = canvas.width;
        tmpCanvas.height = canvas.height;
        var tmpCtx = tmpCanvas.getContext('2d');
        tmpCtx.fillStyle = CHART_BG;
        tmpCtx.fillRect(0, 0, tmpCanvas.width, tmpCanvas.height);
        tmpCtx.drawImage(canvas, 0, 0);
        var link = document.createElement('a');
        link.download = (filename || 'chart') + '.png';
        link.href = tmpCanvas.toDataURL('image/png');
        link.click();
    };
    canvas.parentNode.insertBefore(btn, canvas.nextSibling);
}
