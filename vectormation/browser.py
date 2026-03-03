"""Browser-based SVG viewer for VectorMation.

Serves SVG frames over WebSocket to a self-contained HTML page,
with optional hot-reload support. Includes playback speed control,
FPS display, and keyboard shortcuts for jumping to time percentages.
"""
import asyncio
import json
import logging
import os
import time
import traceback
import webbrowser

import websockets
from websockets import Headers, Response

logger = logging.getLogger('vectormation.browser')

# Module-level singleton to prevent duplicate servers on hot-reload
_active_viewer = None

_HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>VectorMation Viewer</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #1e1e1e; color: #ccc; font-family: monospace;
    display: flex; flex-direction: column; height: 100vh; overflow: hidden;
}
body.bg-white { background: #ffffff; }
body.bg-checker {
    background: repeating-conic-gradient(#808080 0% 25%, #c0c0c0 0% 50%) 50% / 20px 20px;
}
#toolbar, #toolbar2 {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 10px; background: #2d2d2d; border-bottom: 1px solid #444;
    flex-shrink: 0; font-size: 13px;
}
body.toolbars-hidden #toolbar, body.toolbars-hidden #toolbar2 { display: none; }
#toolbar button, #toolbar2 button {
    background: #3c3c3c; color: #ccc; border: 1px solid #555;
    padding: 3px 10px; cursor: pointer; font-family: monospace; font-size: 13px;
}
#toolbar button:hover, #toolbar2 button:hover { background: #505050; }
#progress-wrap {
    flex: 1; height: 16px; background: #3c3c3c; border: 1px solid #555;
    position: relative; min-width: 80px; cursor: pointer;
}
#progress-bar {
    height: 100%; background: #0078d4; width: 0%; transition: width 0.05s linear;
}
#progress-text {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; color: #eee; pointer-events: none;
}
#coords { white-space: nowrap; }
#speed-info { white-space: nowrap; color: #8cf; }
#svg-container {
    flex: 1; overflow: hidden; display: flex;
    align-items: center; justify-content: center;
    position: relative;
}
#svg-content { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
#svg-content svg { max-width: 100%; max-height: 100%; }
#status {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    background: rgba(0,0,0,0.7); color: #ff0; padding: 4px 12px;
    border-radius: 4px; font-size: 13px; display: none; z-index: 10;
}
#error-box {
    position: fixed; top: 40px; left: 50%; transform: translateX(-50%);
    background: #5a1d1d; color: #faa; padding: 8px 16px;
    border-radius: 4px; font-size: 13px; display: none; z-index: 10;
    max-width: 80%; white-space: pre-wrap; border: 1px solid #f66;
}
#btn-snap.active, #btn-loop.active, #btn-grid.active {
    background: #0078d4; color: #fff; border-color: #0078d4;
}
#debug-panel {
    position: fixed; right: 0; top: 0; width: 260px; height: 100vh;
    background: rgba(20,20,20,0.92); color: #ccc; font-family: monospace;
    font-size: 12px; padding: 10px; overflow-y: auto; z-index: 20;
    border-left: 1px solid #444; display: none;
}
#debug-panel h3 { color: #8cf; margin: 0 0 6px 0; font-size: 13px; }
#debug-panel .debug-section { margin-bottom: 8px; }
#debug-panel .obj-item { padding: 1px 0; color: #aaa; }
#help-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.6);
    display: none; z-index: 30; align-items: center; justify-content: center;
}
#help-overlay.visible { display: flex; }
#help-box {
    background: #2d2d2d; border: 1px solid #555; border-radius: 6px;
    padding: 20px 28px; max-width: 480px; width: 90%;
    color: #ccc; font-family: monospace; font-size: 13px;
}
#help-box h3 { color: #8cf; margin: 0 0 12px 0; font-size: 15px; }
#help-box table { width: 100%; border-collapse: collapse; }
#help-box td { padding: 3px 0; }
#help-box td:first-child { color: #ff0; width: 130px; }
#help-box .help-close {
    display: block; text-align: center; margin-top: 14px;
    color: #888; font-size: 12px;
}
#measure-info {
    position: fixed; bottom: 40px; left: 50%; transform: translateX(-50%);
    background: rgba(0,0,0,0.8); color: #0f0; padding: 6px 14px;
    border-radius: 4px; font-size: 13px; display: none; z-index: 10;
}
.bookmark-marker {
    position: absolute; top: 0; width: 2px; height: 100%;
    background: #f80; pointer-events: none; z-index: 1;
}
#inspect-panel {
    position: fixed; left: 0; bottom: 0; max-width: 600px; max-height: 60vh;
    background: rgba(20,20,20,0.92); color: #ccc; font-family: monospace;
    font-size: 12px; padding: 10px; z-index: 20;
    border-top: 1px solid #444; border-right: 1px solid #444;
    display: none;
}
#inspect-panel h3 { color: #8cf; margin: 0 0 6px 0; font-size: 13px; }
#inspect-columns { display: flex; gap: 12px; align-items: flex-start; }
#inspect-col-obj { min-width: 180px; }
#inspect-col-style {
    min-width: 180px; overflow-y: auto;
    border-left: 1px solid #333; padding-left: 10px;
}
#inspect-col-obj::-webkit-scrollbar, #inspect-col-style::-webkit-scrollbar {
    width: 6px;
}
#inspect-col-obj::-webkit-scrollbar-track, #inspect-col-style::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.05);
}
#inspect-col-obj::-webkit-scrollbar-thumb, #inspect-col-style::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2); border-radius: 3px;
}
#inspect-col-obj::-webkit-scrollbar-thumb:hover, #inspect-col-style::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.35);
}
#inspect-col-style h4 { color: #666; margin: 0 0 4px 0; font-size: 11px; }
.inspect-row { padding: 1px 0; cursor: default; }
.inspect-row:hover { background: rgba(255,255,255,0.05); }
.inspect-row.graphable { cursor: pointer; }
.inspect-row.graphable:hover { background: rgba(0,120,212,0.2); }
.inspect-row.selected { background: rgba(0,120,212,0.3); }
.inspect-label { color: #ff0; }
.inspect-value { color: #aaa; }
#inspect-panel .inspect-close {
    position: absolute; top: 4px; right: 8px; cursor: pointer;
    color: #888; font-size: 14px;
}
#graph-panel {
    position: fixed; right: 10px; bottom: 10px;
    background: rgba(20,20,20,0.92); border: 1px solid #444;
    border-radius: 4px; padding: 8px; z-index: 20; display: none;
}
#graph-label {
    color: #8cf; font-family: monospace; font-size: 11px;
    text-align: center; margin-bottom: 4px;
}
#btn-inspect.active { background: #0078d4; color: #fff; border-color: #0078d4; }
#export-menu {
    display: none; position: absolute; top: 100%; left: 0; z-index: 40;
    background: #2d2d2d; border: 1px solid #555; border-radius: 3px;
    min-width: 160px; padding: 2px 0;
}
#export-menu.visible { display: block; }
.export-item {
    padding: 5px 12px; cursor: pointer; font-size: 13px; color: #ccc;
    display: flex; justify-content: space-between; gap: 12px;
}
.export-item:hover { background: #505050; }
.export-key { color: #888; font-size: 11px; }
</style>
</head>
<body>
<div id="toolbar">
    <button id="btn-restart" title="Restart (R)">Restart</button>
    <button id="btn-pause" title="Pause (P)">Pause</button>
    <button id="btn-slower" title="Slow Down (-)">-</button>
    <button id="btn-faster" title="Speed Up (+)">+</button>
    <span id="speed-info">1.0x</span>
    <div id="progress-wrap">
        <div id="progress-bar"></div>
        <div id="progress-text">0.00s / 0.00s</div>
    </div>
    <span id="coords">x=? y=?</span>
</div>
<div id="toolbar2">
    <button id="btn-fit" title="Reset Zoom (F)">Reset Zoom</button>
    <button id="btn-snap" title="Toggle Snap (N)">Snap: OFF</button>
    <button id="btn-loop" title="Toggle Loop (L)">Loop: OFF</button>
    <button id="btn-grid" title="Toggle Grid (G)">Grid: OFF</button>
    <button id="btn-inspect" title="Inspect Mode (I)">Inspect: OFF</button>
    <div style="position:relative;display:inline-block;">
        <button id="btn-export" title="Export (S)">Export &#9662;</button>
        <div id="export-menu">
            <div class="export-item" id="exp-svg">Save SVG <span class="export-key">S</span></div>
            <div class="export-item" id="exp-png">Save PNG <span class="export-key">Shift+S</span></div>
            <div class="export-item" id="exp-copy">Copy SVG <span class="export-key">C</span></div>
        </div>
    </div>
    <span style="flex:1"></span>
    <button id="btn-help" title="Keyboard Shortcuts (?)">?</button>
</div>
<div id="svg-container">
    <div id="svg-content"></div>
</div>
<div id="status"></div>
<div id="error-box"></div>
<div id="measure-info"></div>
<div id="help-overlay">
<div id="help-box">
    <h3>Keyboard Shortcuts</h3>
    <table>
    <tr><td>Space / P</td><td>Pause / Resume</td></tr>
    <tr><td>R</td><td>Restart</td></tr>
    <tr><td>, / .</td><td>Step backward / forward</td></tr>
    <tr><td>&larr; / &rarr;</td><td>Prev section / Next section</td></tr>
    <tr><td>- / + / &uarr; / &darr;</td><td>Slower / Faster</td></tr>
    <tr><td>0 &ndash; 9</td><td>Jump to 0% &ndash; 90%</td></tr>
    <tr><td>Home / End</td><td>Jump to start / end</td></tr>
    <tr><td>F</td><td>Reset zoom</td></tr>
    <tr><td>S</td><td>Save SVG</td></tr>
    <tr><td>Shift+S</td><td>Save PNG</td></tr>
    <tr><td>C</td><td>Copy SVG to clipboard</td></tr>
    <tr><td>L</td><td>Toggle loop</td></tr>
    <tr><td>B</td><td>Cycle background (dark/white/checker)</td></tr>
    <tr><td>H</td><td>Hide/show toolbars</td></tr>
    <tr><td>G</td><td>Toggle grid overlay</td></tr>
    <tr><td>M</td><td>Measure tool (click two points)</td></tr>
    <tr><td>N</td><td>Toggle snap</td></tr>
    <tr><td>D</td><td>Debug panel</td></tr>
    <tr><td>Ctrl+B</td><td>Add/remove bookmark</td></tr>
    <tr><td>[ / ]</td><td>Prev / next bookmark</td></tr>
    <tr><td>I</td><td>Inspect mode (nearest object)</td></tr>
    <tr><td>Q</td><td>Quit</td></tr>
    </table>
    <span class="help-close">Press any key or click to close</span>
</div>
</div>
<div id="inspect-panel">
    <span class="inspect-close" id="inspect-close">&times;</span>
    <h3 id="inspect-title">Object Inspector</h3>
    <div id="inspect-columns">
        <div id="inspect-col-obj"></div>
        <div id="inspect-col-style"><h4>Styling</h4><div id="inspect-style-content"></div></div>
    </div>
</div>
<div id="graph-panel">
    <div id="graph-label"></div>
    <canvas id="attr-graph"></canvas>
</div>
<div id="debug-panel">
    <h3>Timeline Inspector</h3>
    <div class="debug-section" id="debug-time"></div>
    <div class="debug-section" id="debug-frame"></div>
    <div class="debug-section"><b>Visible Objects:</b></div>
    <div id="debug-objects"></div>
</div>
<script>
(function() {
    const container = document.getElementById('svg-container');
    const svgContent = document.getElementById('svg-content');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressWrap = document.getElementById('progress-wrap');
    const coordsEl = document.getElementById('coords');
    const statusEl = document.getElementById('status');
    const errorEl = document.getElementById('error-box');
    const btnPause = document.getElementById('btn-pause');
    const speedInfo = document.getElementById('speed-info');
    const debugPanel = document.getElementById('debug-panel');
    const debugTime = document.getElementById('debug-time');
    const debugFrame = document.getElementById('debug-frame');
    const debugObjects = document.getElementById('debug-objects');
    const measureInfo = document.getElementById('measure-info');
    const inspectPanel = document.getElementById('inspect-panel');
    const inspectTitle = document.getElementById('inspect-title');
    const inspectColObj = document.getElementById('inspect-col-obj');
    const inspectStyleContent = document.getElementById('inspect-style-content');
    const graphPanel = document.getElementById('graph-panel');
    const graphCanvas = document.getElementById('attr-graph');
    const graphLabel = document.getElementById('graph-label');
    const btnInspect = document.getElementById('btn-inspect');
    let ws = null;
    let paused = false;
    let currentViewbox = null;
    let statusTimeout = null;
    let currentSpeed = 1.0;
    let currentTime = 0;
    let currentStartTime = 0;
    let currentEndTime = 0;
    let snapEnabled = false;
    let snapPoints = [];
    let debugVisible = false;
    let loopEnabled = false;
    let gridVisible = false;
    let bgMode = 0; // 0=dark, 1=white, 2=checker
    let measureMode = false;
    let measurePoint1 = null; // {x, y} in SVG coords
    let bookmarks = []; // sorted list of bookmarked times
    let objectsInfo = []; // latest objects_info from server
    let inspectedIdx = -1; // currently inspected object index
    let inspectMode = false; // inspect mode: hover highlights nearest
    let selectedAttr = ''; // currently graphed attribute
    let lastGraphMsg = null; // last graph data for redraw
    const btnSnap = document.getElementById('btn-snap');
    const btnLoop = document.getElementById('btn-loop');
    const btnGrid = document.getElementById('btn-grid');
    const SNAP_THRESHOLD_PX = 15;
    const UNIT = 135;

    function connect() {
        const loc = window.location;
        ws = new WebSocket('ws://' + loc.host + '/ws');
        ws.onopen = function() {
            hideError(); showStatus('Connected');
            if (snapEnabled) send({type: 'control', action: 'snap_enable'});
        };
        ws.onmessage = function(evt) {
            const msg = JSON.parse(evt.data);
            if (msg.type === 'frame') {
                svgContent.innerHTML = msg.svg;
                currentViewbox = msg.viewbox;
                var t = msg.time !== undefined ? msg.time : 0;
                var endT = msg.end !== undefined ? msg.end : 0;
                var startT = msg.start !== undefined ? msg.start : 0;
                currentTime = t;
                currentStartTime = startT;
                currentEndTime = endT;
                var duration = endT - startT;
                var pct = duration > 0 ? ((t - startT) / duration * 100) : 100;
                progressBar.style.width = Math.min(100, Math.max(0, pct)) + '%';
                progressText.textContent = t.toFixed(2) + 's / ' + endT.toFixed(2) + 's';
                if (msg.speed !== undefined) currentSpeed = msg.speed;
                speedInfo.textContent = currentSpeed.toFixed(1) + 'x';
                if (msg.snap_points !== undefined) snapPoints = msg.snap_points;
                if (msg.loop !== undefined && msg.loop !== loopEnabled) {
                    loopEnabled = msg.loop;
                    btnLoop.textContent = 'Loop: ' + (loopEnabled ? 'ON' : 'OFF');
                    btnLoop.classList.toggle('active', loopEnabled);
                }
                if (msg.objects_info) objectsInfo = msg.objects_info;
                if (debugVisible) {
                    debugTime.textContent = 'Time: ' + t.toFixed(3) + 's';
                    debugFrame.textContent = 'Frame: ' + (msg.frame || 0) + ' / ' + (msg.total_frames || 0);
                    debugObjects.innerHTML = objectsInfo.map(function(o, i) {
                        return '<div class="obj-item">' + i + ': ' + o['class'] + (o.name ? ' "' + o.name + '"' : '') + '</div>';
                    }).join('');
                }
                if (gridVisible) renderGrid();
                renderMeasureOverlay();
                renderBookmarkMarkers();
                // Re-highlight inspected object if panel is open
                if (inspectedIdx >= 0 && inspectPanel.style.display === 'block') {
                    highlightObject(inspectedIdx);
                    // Redraw graph with updated current time cursor
                    if (lastGraphMsg && graphPanel.style.display === 'block') {
                        drawAttrGraph(lastGraphMsg);
                    }
                }
            } else if (msg.type === 'inspect_result') {
                showInspectResult(msg);
            } else if (msg.type === 'inspect_graph') {
                drawAttrGraph(msg);
            } else if (msg.type === 'status') {
                showStatus(msg.message);
            } else if (msg.type === 'error') {
                showError(msg.message);
            }
        };
        ws.onclose = function() {
            showStatus('Disconnected \u2014 reconnecting...');
            setTimeout(connect, 300);
        };
    }

    function send(obj) {
        if (ws && ws.readyState === WebSocket.OPEN)
            ws.send(JSON.stringify(obj));
    }

    function showStatus(msg) {
        statusEl.textContent = msg;
        statusEl.style.display = 'block';
        clearTimeout(statusTimeout);
        statusTimeout = setTimeout(function() {
            statusEl.style.display = 'none';
        }, 2000);
    }

    function showError(msg) {
        errorEl.textContent = msg;
        errorEl.style.display = 'block';
    }

    function hideError() {
        errorEl.style.display = 'none';
    }

    function saveSvg() {
        const svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        const xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgEl.outerHTML;
        const blob = new Blob([xml], {type: 'image/svg+xml'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'frame.svg';
        a.click();
        URL.revokeObjectURL(a.href);
        showStatus('SVG saved');
    }

    function savePng() {
        const svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        var vb = currentViewbox || [0, 0, 1920, 1080];
        var w = vb[2], h = vb[3];
        var xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgEl.outerHTML;
        var blob = new Blob([xml], {type: 'image/svg+xml;charset=utf-8'});
        var url = URL.createObjectURL(blob);
        var img = new Image();
        img.onload = function() {
            var canvas = document.createElement('canvas');
            canvas.width = w; canvas.height = h;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, w, h);
            URL.revokeObjectURL(url);
            canvas.toBlob(function(pngBlob) {
                var a = document.createElement('a');
                a.href = URL.createObjectURL(pngBlob);
                a.download = 'frame.png';
                a.click();
                URL.revokeObjectURL(a.href);
                showStatus('PNG saved');
            }, 'image/png');
        };
        img.onerror = function() {
            URL.revokeObjectURL(url);
            showStatus('PNG export failed');
        };
        img.src = url;
    }

    function copySvg() {
        const svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        var xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgEl.outerHTML;
        navigator.clipboard.writeText(xml).then(function() {
            showStatus('SVG copied to clipboard');
        }, function() {
            showStatus('Copy failed');
        });
    }

    function changeSpeed(delta) {
        currentSpeed = Math.max(0.1, Math.round((currentSpeed + delta) * 10) / 10);
        send({type: 'control', action: 'speed', value: currentSpeed});
        showStatus('Speed: ' + currentSpeed.toFixed(1) + 'x');
    }

    // Progress bar: click and drag to scrub
    var scrubbing = false;
    function scrubTo(e) {
        var rect = progressWrap.getBoundingClientRect();
        var pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        send({type: 'control', action: 'jump', percentage: pct});
    }
    progressWrap.addEventListener('mousedown', function(e) {
        scrubbing = true;
        scrubTo(e);
    });
    document.addEventListener('mousemove', function(e) {
        if (scrubbing) scrubTo(e);
    });
    document.addEventListener('mouseup', function() {
        scrubbing = false;
    });

    document.getElementById('btn-restart').addEventListener('click', function() {
        send({type: 'control', action: 'restart'});
    });
    function togglePause() {
        paused = !paused;
        btnPause.textContent = paused ? 'Resume' : 'Pause';
        send({type: 'control', action: 'pause'});
    }
    btnPause.addEventListener('click', togglePause);
    // Export dropdown
    var exportMenu = document.getElementById('export-menu');
    document.getElementById('btn-export').addEventListener('click', function(e) {
        e.stopPropagation();
        exportMenu.classList.toggle('visible');
    });
    document.addEventListener('click', function() { exportMenu.classList.remove('visible'); });
    document.getElementById('exp-svg').addEventListener('click', function() { exportMenu.classList.remove('visible'); saveSvg(); });
    document.getElementById('exp-png').addEventListener('click', function() { exportMenu.classList.remove('visible'); savePng(); });
    document.getElementById('exp-copy').addEventListener('click', function() { exportMenu.classList.remove('visible'); copySvg(); });
    document.getElementById('btn-fit').addEventListener('click', function() {
        send({type: 'control', action: 'fit'});
    });
    document.getElementById('btn-slower').addEventListener('click', function() {
        changeSpeed(-0.25);
    });
    document.getElementById('btn-faster').addEventListener('click', function() {
        changeSpeed(0.25);
    });

    function toggleSnap() {
        snapEnabled = !snapEnabled;
        btnSnap.textContent = 'Snap: ' + (snapEnabled ? 'ON' : 'OFF');
        btnSnap.classList.toggle('active', snapEnabled);
        send({type: 'control', action: 'snap_toggle'});
        if (!snapEnabled) removeSnapIndicator();
        showStatus('Snap ' + (snapEnabled ? 'enabled' : 'disabled'));
    }
    btnSnap.addEventListener('click', toggleSnap);

    function toggleLoop() {
        loopEnabled = !loopEnabled;
        btnLoop.textContent = 'Loop: ' + (loopEnabled ? 'ON' : 'OFF');
        btnLoop.classList.toggle('active', loopEnabled);
        send({type: 'control', action: 'loop_toggle'});
        showStatus('Loop ' + (loopEnabled ? 'enabled' : 'disabled'));
    }
    btnLoop.addEventListener('click', toggleLoop);

    function toggleGrid() {
        gridVisible = !gridVisible;
        btnGrid.textContent = 'Grid: ' + (gridVisible ? 'ON' : 'OFF');
        btnGrid.classList.toggle('active', gridVisible);
        if (!gridVisible) removeGrid();
        showStatus('Grid ' + (gridVisible ? 'ON' : 'OFF'));
    }
    btnGrid.addEventListener('click', toggleGrid);

    function removeGrid() {
        var old = document.getElementById('_grid_overlay');
        if (old) old.remove();
    }

    function renderGrid() {
        removeGrid();
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl || !currentViewbox) return;
        var ns = 'http://www.w3.org/2000/svg';
        var g = document.createElementNS(ns, 'g');
        g.setAttribute('id', '_grid_overlay');
        g.setAttribute('pointer-events', 'none');
        // ORIGIN = (960, 540), UNIT = 135
        var ox = 960, oy = 540;
        var vb = currentViewbox;
        var sw = Math.min(vb[2], vb[3]) * 0.001;
        var swThick = sw * 2.5;
        // Draw unit grid lines
        var left = Math.floor((vb[0] - ox) / UNIT) * UNIT;
        var right = Math.ceil((vb[0] + vb[2] - ox) / UNIT) * UNIT;
        var top_ = Math.floor((vb[1] - oy) / UNIT) * UNIT;
        var bottom = Math.ceil((vb[1] + vb[3] - oy) / UNIT) * UNIT;
        for (var gx = left; gx <= right; gx += UNIT) {
            var line = document.createElementNS(ns, 'line');
            line.setAttribute('x1', ox + gx); line.setAttribute('y1', vb[1]);
            line.setAttribute('x2', ox + gx); line.setAttribute('y2', vb[1] + vb[3]);
            var isAxis = (gx === 0);
            line.setAttribute('stroke', isAxis ? 'rgba(255,100,100,0.5)' : 'rgba(255,255,255,0.15)');
            line.setAttribute('stroke-width', isAxis ? swThick : sw);
            g.appendChild(line);
        }
        for (var gy = top_; gy <= bottom; gy += UNIT) {
            var line = document.createElementNS(ns, 'line');
            line.setAttribute('x1', vb[0]); line.setAttribute('y1', oy + gy);
            line.setAttribute('x2', vb[0] + vb[2]); line.setAttribute('y2', oy + gy);
            var isAxis = (gy === 0);
            line.setAttribute('stroke', isAxis ? 'rgba(255,100,100,0.5)' : 'rgba(255,255,255,0.15)');
            line.setAttribute('stroke-width', isAxis ? swThick : sw);
            g.appendChild(line);
        }
        // Origin crosshair dot
        var dot = document.createElementNS(ns, 'circle');
        dot.setAttribute('cx', ox); dot.setAttribute('cy', oy);
        dot.setAttribute('r', swThick * 3);
        dot.setAttribute('fill', 'rgba(255,100,100,0.7)');
        g.appendChild(dot);
        svgEl.appendChild(g);
    }

    function removeSnapIndicator() {
        var old = document.getElementById('_snap_ind');
        if (old) old.remove();
    }

    function showSnapIndicator(svgX, svgY) {
        removeSnapIndicator();
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl || !currentViewbox) return;
        var vb = currentViewbox;
        var r = Math.min(vb[2], vb[3]) * 0.015;
        var arm = r * 1.8;
        var sw = r * 0.3;
        var ns = 'http://www.w3.org/2000/svg';
        var g = document.createElementNS(ns, 'g');
        g.setAttribute('id', '_snap_ind');
        var circle = document.createElementNS(ns, 'circle');
        circle.setAttribute('cx', svgX); circle.setAttribute('cy', svgY);
        circle.setAttribute('r', r);
        circle.setAttribute('fill', 'rgba(255,255,0,0.25)');
        circle.setAttribute('stroke', '#ff0'); circle.setAttribute('stroke-width', sw);
        g.appendChild(circle);
        var l1 = document.createElementNS(ns, 'line');
        l1.setAttribute('x1', svgX - arm); l1.setAttribute('y1', svgY);
        l1.setAttribute('x2', svgX + arm); l1.setAttribute('y2', svgY);
        l1.setAttribute('stroke', '#ff0'); l1.setAttribute('stroke-width', sw);
        g.appendChild(l1);
        var l2 = document.createElementNS(ns, 'line');
        l2.setAttribute('x1', svgX); l2.setAttribute('y1', svgY - arm);
        l2.setAttribute('x2', svgX); l2.setAttribute('y2', svgY + arm);
        l2.setAttribute('stroke', '#ff0'); l2.setAttribute('stroke-width', sw);
        g.appendChild(l2);
        svgEl.appendChild(g);
    }

    // Measure tool
    function removeMeasureOverlay() {
        var old = document.getElementById('_measure_overlay');
        if (old) old.remove();
    }

    function renderMeasureOverlay() {
        removeMeasureOverlay();
        if (!measurePoint1) return;
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl || !currentViewbox) return;
        var ns = 'http://www.w3.org/2000/svg';
        var vb = currentViewbox;
        var sw = Math.min(vb[2], vb[3]) * 0.003;
        var r = sw * 2;
        var g = document.createElementNS(ns, 'g');
        g.setAttribute('id', '_measure_overlay');
        g.setAttribute('pointer-events', 'none');
        // Point 1 dot
        var d1 = document.createElementNS(ns, 'circle');
        d1.setAttribute('cx', measurePoint1.x); d1.setAttribute('cy', measurePoint1.y);
        d1.setAttribute('r', r); d1.setAttribute('fill', '#0f0');
        g.appendChild(d1);
        svgEl.appendChild(g);
    }

    function finishMeasure(p2) {
        var p1 = measurePoint1;
        var dx = p2.x - p1.x, dy = p2.y - p1.y;
        var distPx = Math.sqrt(dx*dx + dy*dy);
        var distUnits = distPx / UNIT;
        measureInfo.textContent = 'Distance: ' + distPx.toFixed(1) + 'px = ' + distUnits.toFixed(3) + ' units';
        measureInfo.style.display = 'block';
        // Draw line + second dot
        var svgEl = svgContent.querySelector('svg');
        if (svgEl && currentViewbox) {
            var ns = 'http://www.w3.org/2000/svg';
            removeMeasureOverlay();
            var vb = currentViewbox;
            var sw = Math.min(vb[2], vb[3]) * 0.003;
            var r = sw * 2;
            var g = document.createElementNS(ns, 'g');
            g.setAttribute('id', '_measure_overlay');
            g.setAttribute('pointer-events', 'none');
            var line = document.createElementNS(ns, 'line');
            line.setAttribute('x1', p1.x); line.setAttribute('y1', p1.y);
            line.setAttribute('x2', p2.x); line.setAttribute('y2', p2.y);
            line.setAttribute('stroke', '#0f0'); line.setAttribute('stroke-width', sw);
            line.setAttribute('stroke-dasharray', sw * 3 + ',' + sw * 2);
            g.appendChild(line);
            var d1 = document.createElementNS(ns, 'circle');
            d1.setAttribute('cx', p1.x); d1.setAttribute('cy', p1.y);
            d1.setAttribute('r', r); d1.setAttribute('fill', '#0f0');
            g.appendChild(d1);
            var d2 = document.createElementNS(ns, 'circle');
            d2.setAttribute('cx', p2.x); d2.setAttribute('cy', p2.y);
            d2.setAttribute('r', r); d2.setAttribute('fill', '#0f0');
            g.appendChild(d2);
            svgEl.appendChild(g);
        }
        measurePoint1 = null;
        measureMode = false;
    }

    function clientToSvg(svgEl, clientX, clientY) {
        var ctm = svgEl.getScreenCTM();
        if (!ctm) return null;
        var inv = ctm.inverse();
        return { x: inv.a * clientX + inv.c * clientY + inv.e,
                 y: inv.b * clientX + inv.d * clientY + inv.f };
    }

    function svgToClient(svgEl, svgX, svgY) {
        var ctm = svgEl.getScreenCTM();
        if (!ctm) return null;
        return { x: ctm.a * svgX + ctm.c * svgY + ctm.e,
                 y: ctm.b * svgX + ctm.d * svgY + ctm.f };
    }

    function findNearestSnap(svgEl, mouseClientX, mouseClientY) {
        var best = null, bestDist = Infinity;
        for (var i = 0; i < snapPoints.length; i++) {
            var sp = snapPoints[i];
            var screen = svgToClient(svgEl, sp[0], sp[1]);
            if (!screen) continue;
            var dx = mouseClientX - screen.x, dy = mouseClientY - screen.y;
            var dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < bestDist) { bestDist = dist; best = {svgX: sp[0], svgY: sp[1]}; }
        }
        if (best && bestDist <= SNAP_THRESHOLD_PX) return best;
        return null;
    }

    var helpOverlay = document.getElementById('help-overlay');
    function toggleHelp() {
        helpOverlay.classList.toggle('visible');
    }
    document.getElementById('btn-help').addEventListener('click', toggleHelp);
    helpOverlay.addEventListener('click', function() { helpOverlay.classList.remove('visible'); });

    function cycleBg() {
        document.body.classList.remove('bg-white', 'bg-checker');
        bgMode = (bgMode + 1) % 3;
        if (bgMode === 1) { document.body.classList.add('bg-white'); showStatus('Background: white'); }
        else if (bgMode === 2) { document.body.classList.add('bg-checker'); showStatus('Background: checker'); }
        else { showStatus('Background: dark'); }
    }

    // Bookmarks
    function toggleBookmark() {
        var t = Math.round(currentTime * 1000) / 1000;
        var idx = bookmarks.indexOf(t);
        if (idx >= 0) {
            bookmarks.splice(idx, 1);
            showStatus('Bookmark removed: t=' + t.toFixed(3) + 's (' + bookmarks.length + ' total)');
        } else {
            bookmarks.push(t);
            bookmarks.sort(function(a, b) { return a - b; });
            showStatus('Bookmark added: t=' + t.toFixed(3) + 's (' + bookmarks.length + ' total)');
        }
        console.log('[VectorMation] Bookmarks:', bookmarks.map(function(b) { return b.toFixed(3) + 's'; }).join(', '));
        renderBookmarkMarkers();
    }

    function jumpToBookmark(dir) {
        if (bookmarks.length === 0) { showStatus('No bookmarks'); return; }
        var t = currentTime;
        var target = null;
        if (dir > 0) {
            for (var i = 0; i < bookmarks.length; i++) {
                if (bookmarks[i] > t + 0.001) { target = bookmarks[i]; break; }
            }
            if (target === null) target = bookmarks[0]; // wrap around
        } else {
            for (var i = bookmarks.length - 1; i >= 0; i--) {
                if (bookmarks[i] < t - 0.001) { target = bookmarks[i]; break; }
            }
            if (target === null) target = bookmarks[bookmarks.length - 1]; // wrap around
        }
        var duration = currentEndTime - currentStartTime;
        if (duration > 0) {
            var pct = (target - currentStartTime) / duration;
            send({type: 'control', action: 'jump', percentage: pct});
            showStatus('Bookmark: t=' + target.toFixed(3) + 's');
        }
    }

    function renderBookmarkMarkers() {
        // Remove old markers
        progressWrap.querySelectorAll('.bookmark-marker').forEach(function(m) { m.remove(); });
        if (bookmarks.length === 0) return;
        var duration = currentEndTime - currentStartTime;
        if (duration <= 0) return;
        bookmarks.forEach(function(t) {
            var pct = (t - currentStartTime) / duration * 100;
            if (pct < 0 || pct > 100) return;
            var marker = document.createElement('div');
            marker.className = 'bookmark-marker';
            marker.style.left = pct + '%';
            marker.title = 't=' + t.toFixed(3) + 's';
            progressWrap.appendChild(marker);
        });
    }

    // Object inspection

    // Find the nearest object to a point (by center distance)
    function findNearestObject(svgX, svgY) {
        var bestIdx = -1, bestDist = Infinity;
        for (var i = 0; i < objectsInfo.length; i++) {
            var info = objectsInfo[i];
            if (!info.center) continue;
            var dx = svgX - info.center[0], dy = svgY - info.center[1];
            var dist = dx*dx + dy*dy;
            if (dist < bestDist) { bestDist = dist; bestIdx = i; }
        }
        return bestIdx;
    }

    // Find the topmost object whose bbox contains the point
    function findObjectAtPoint(svgX, svgY) {
        for (var i = objectsInfo.length - 1; i >= 0; i--) {
            var info = objectsInfo[i];
            if (!info.bbox) continue;
            var bx = info.bbox[0], by = info.bbox[1], bw = info.bbox[2], bh = info.bbox[3];
            if (svgX >= bx && svgX <= bx + bw && svgY >= by && svgY <= by + bh) return i;
        }
        return -1;
    }

    function selectObject(idx) {
        if (idx < 0 || idx >= objectsInfo.length) return;
        inspectedIdx = idx;
        selectedAttr = '';
        lastGraphMsg = null;
        graphPanel.style.display = 'none';
        send({type: 'control', action: 'inspect_object', idx: idx});
        highlightObject(idx);
    }

    function renderAttrRows(attrs) {
        var lines = [];
        for (var a = 0; a < attrs.length; a++) {
            var attr = attrs[a];
            var name = attr.name;
            var graphable = attr.type !== 'info';
            var cls = 'inspect-row' + (graphable ? ' graphable' : '');
            var sel = (name === selectedAttr) ? ' selected' : '';
            var colorSwatch = '';
            if (attr.type === 'color' && attr.value.match && attr.value.match(/^rgb/)) {
                colorSwatch = '<span style="display:inline-block;width:10px;height:10px;border:1px solid #555;vertical-align:middle;margin-left:4px;background:' + attr.value + '"></span>';
            }
            var displayName = name.replace('style.', '');
            lines.push('<div class="' + cls + sel + '" data-attr="' + name + '">' +
                '<span class="inspect-label">' + displayName + ':</span> ' +
                '<span class="inspect-value">' + attr.value + '</span>' + colorSwatch + '</div>');
        }
        return lines.join('');
    }

    function bindGraphClicks(container) {
        container.querySelectorAll('.graphable').forEach(function(row) {
            row.addEventListener('click', function() {
                var attr = row.dataset.attr;
                if (!attr || inspectedIdx < 0) return;
                selectedAttr = attr;
                inspectPanel.querySelectorAll('.inspect-row').forEach(function(r) { r.classList.remove('selected'); });
                row.classList.add('selected');
                send({type: 'control', action: 'inspect_attribute', idx: inspectedIdx, attr: attr});
            });
        });
    }

    function showInspectResult(msg) {
        inspectTitle.textContent = msg['class'] + ' #' + msg.idx;
        inspectColObj.innerHTML = renderAttrRows(msg.obj_attrs || []);
        inspectStyleContent.innerHTML = renderAttrRows(msg.style_attrs || []);
        inspectPanel.style.display = 'block';
        // Constrain style column height to match obj column
        var inspectColStyle = document.getElementById('inspect-col-style');
        inspectColStyle.style.maxHeight = '';
        requestAnimationFrame(function() {
            inspectColStyle.style.maxHeight = inspectColObj.offsetHeight + 'px';
        });
        bindGraphClicks(inspectColObj);
        bindGraphClicks(inspectStyleContent);
    }

    function fmtTick(v) {
        // Smart tick formatting: avoid trailing zeros, keep it short
        if (Math.abs(v) >= 1000) return v.toFixed(0);
        if (Math.abs(v) >= 100) return v.toFixed(0);
        if (Math.abs(v) >= 10) return v.toFixed(1);
        return v.toFixed(1);
    }

    function drawAttrGraphStacked(msg, series, times, minT, maxT, dpr) {
        var labels = msg.labels || null;
        var graphH = 74, padL = 50, padR = 30, W = 340;
        var cssH = series.length * graphH + 16; // +16 for time axis
        graphCanvas.style.width = W + 'px';
        graphCanvas.style.height = cssH + 'px';
        graphCanvas.width = W * dpr;
        graphCanvas.height = cssH * dpr;
        var ctx = graphCanvas.getContext('2d');
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, W, cssH);
        graphPanel.style.display = 'block';
        graphLabel.textContent = msg.attr;

        var tx = function(t) { return padL + (t - minT) / (maxT - minT) * (W - padL - padR); };

        for (var s = 0; s < series.length; s++) {
            var ser = series[s];
            var lbl = (labels && labels[s]) ? labels[s] : ser.label;
            var yOff = s * graphH;
            var plotH = graphH - 14;

            var minV = Infinity, maxV = -Infinity;
            for (var i = 0; i < ser.values.length; i++) {
                if (ser.values[i] < minV) minV = ser.values[i];
                if (ser.values[i] > maxV) maxV = ser.values[i];
            }
            var range = maxV - minV;
            if (range === 0) { range = 2; minV -= 1; maxV += 1; }
            else { var margin = range * 0.08; minV -= margin; maxV += margin; }

            var _minV = minV, _maxV = maxV, _yOff = yOff, _plotH = plotH;
            function makeTy(mn, mx, yo, ph) {
                return function(v) { return yo + 6 + ph - (v - mn) / (mx - mn) * ph; };
            }
            var ty = makeTy(_minV, _maxV, _yOff, _plotH);

            // Axis
            ctx.strokeStyle = '#444'; ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(padL, yOff + 4); ctx.lineTo(padL, yOff + 6 + plotH);
            ctx.lineTo(W - padR, yOff + 6 + plotH);
            ctx.stroke();

            // Component label
            ctx.fillStyle = ser.color; ctx.font = '10px monospace'; ctx.textAlign = 'left';
            ctx.fillText(lbl, 2, yOff + 13);
            // Y-axis ticks
            ctx.fillStyle = '#666'; ctx.font = '9px monospace'; ctx.textAlign = 'right';
            ctx.fillText(fmtTick(maxV), padL - 3, yOff + 13);
            ctx.fillText(fmtTick(minV), padL - 3, yOff + 6 + plotH);

            // Current time indicator
            if (currentTime >= minT && currentTime <= maxT) {
                var cx = tx(currentTime);
                ctx.strokeStyle = 'rgba(255,255,0,0.3)'; ctx.lineWidth = 1;
                ctx.beginPath(); ctx.moveTo(cx, yOff + 4); ctx.lineTo(cx, yOff + 6 + plotH); ctx.stroke();
            }

            // Plot line
            ctx.strokeStyle = ser.color; ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(tx(times[0]), ty(ser.values[0]));
            for (var i = 1; i < times.length; i++) {
                ctx.lineTo(tx(times[i]), ty(ser.values[i]));
            }
            ctx.stroke();
        }

        // Time axis labels (below all graphs)
        var tY = series.length * graphH + 10;
        ctx.fillStyle = '#888'; ctx.font = '10px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(minT.toFixed(1) + 's', padL, tY);
        ctx.textAlign = 'right';
        ctx.fillText(maxT.toFixed(1) + 's', W - padR, tY);
    }

    function drawAttrGraphSingle(msg, times, data, kind, minT, maxT, dpr) {
        var padL = 50, padR = 30, padB = 22;
        var W = 340, H = (kind === 'color') ? 50 : (kind === 'string') ? 80 : 150;
        graphCanvas.style.width = W + 'px';
        graphCanvas.style.height = H + 'px';
        graphCanvas.width = W * dpr;
        graphCanvas.height = H * dpr;
        var ctx = graphCanvas.getContext('2d');
        ctx.scale(dpr, dpr);

        graphPanel.style.display = 'block';
        graphLabel.textContent = msg.attr;

        var tx = function(t) { return padL + (t - minT) / (maxT - minT) * (W - padL - padR); };

        ctx.clearRect(0, 0, W, H);

        if (kind === 'color') {
            var slabH = H - 18;
            for (var i = 0; i < data.length; i++) {
                var x1 = tx(times[i]);
                var x2 = (i + 1 < times.length) ? tx(times[i + 1]) : x1 + 1;
                ctx.fillStyle = 'rgb(' + data[i][0] + ',' + data[i][1] + ',' + data[i][2] + ')';
                ctx.fillRect(x1, 2, Math.max(x2 - x1, 1), slabH);
            }
            ctx.fillStyle = '#888'; ctx.font = '10px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(minT.toFixed(1) + 's', padL, H - 2);
            ctx.textAlign = 'right';
            ctx.fillText(maxT.toFixed(1) + 's', W - padR, H - 2);
            if (currentTime >= minT && currentTime <= maxT) {
                var cx = tx(currentTime);
                ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(cx, 0); ctx.lineTo(cx, slabH + 2); ctx.stroke();
            }

        } else if (kind === 'string') {
            var bandH = Math.max(H - 28, 20);
            var uniq = []; var valMap = {};
            for (var i = 0; i < data.length; i++) {
                if (valMap[data[i]] === undefined) { valMap[data[i]] = uniq.length; uniq.push(data[i]); }
            }
            var colors = ['#0ff', '#f80', '#8f0', '#f0f', '#08f', '#ff0', '#f00', '#0f8'];
            for (var i = 0; i < data.length; i++) {
                var x1 = tx(times[i]);
                var x2 = (i + 1 < times.length) ? tx(times[i + 1]) : x1 + 2;
                ctx.fillStyle = colors[valMap[data[i]] % colors.length];
                ctx.fillRect(x1, 5, Math.max(x2 - x1, 1), bandH);
            }
            ctx.fillStyle = '#888'; ctx.font = '10px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(minT.toFixed(1) + 's', padL, H - 2);
            ctx.textAlign = 'right';
            ctx.fillText(maxT.toFixed(1) + 's', W - padR, H - 2);
            if (currentTime >= minT && currentTime <= maxT) {
                var cx = tx(currentTime);
                ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(cx, 0); ctx.lineTo(cx, bandH + 5); ctx.stroke();
                var curIdx = 0;
                for (var i = 0; i < times.length; i++) { if (times[i] <= currentTime) curIdx = i; }
                ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.font = '10px monospace';
                ctx.fillText(data[curIdx], cx, H - 12);
            }

        } else {
            // Single real series
            var plotTop = 8;
            var plotBot = H - padB;
            var vals = [];
            for (var i = 0; i < data.length; i++) vals.push(Array.isArray(data[i]) ? data[i][0] : data[i]);

            var minV = Infinity, maxV = -Infinity;
            for (var i = 0; i < vals.length; i++) {
                if (vals[i] < minV) minV = vals[i];
                if (vals[i] > maxV) maxV = vals[i];
            }
            var range = maxV - minV;
            if (range === 0) { range = 2; minV -= 1; maxV += 1; }
            else { var margin = range * 0.08; minV -= margin; maxV += margin; }

            var ty = function(v) { return plotBot - (v - minV) / (maxV - minV) * (plotBot - plotTop); };

            // Axes
            ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(padL, plotTop); ctx.lineTo(padL, plotBot); ctx.lineTo(W - padR, plotBot);
            ctx.stroke();

            // Y-axis ticks
            ctx.fillStyle = '#888'; ctx.font = '10px monospace';
            ctx.textAlign = 'right';
            ctx.fillText(fmtTick(maxV), padL - 3, plotTop + 4);
            ctx.fillText(fmtTick(minV), padL - 3, plotBot);

            // Time axis labels
            ctx.textAlign = 'left';
            ctx.fillText(minT.toFixed(1) + 's', padL, H - 4);
            ctx.textAlign = 'right';
            ctx.fillText(maxT.toFixed(1) + 's', W - padR, H - 4);

            // Current time indicator
            if (currentTime >= minT && currentTime <= maxT) {
                var cx = tx(currentTime);
                ctx.strokeStyle = 'rgba(255,255,0,0.4)'; ctx.lineWidth = 1;
                ctx.beginPath(); ctx.moveTo(cx, plotTop); ctx.lineTo(cx, plotBot); ctx.stroke();
            }

            ctx.strokeStyle = '#0ff'; ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(tx(times[0]), ty(vals[0]));
            for (var i = 1; i < times.length; i++) {
                ctx.lineTo(tx(times[i]), ty(vals[i]));
            }
            ctx.stroke();
        }
    }

    function drawAttrGraph(msg) {
        lastGraphMsg = msg;
        var times = msg.times, data = msg.data, kind = msg.kind;
        if (!times || !data || times.length < 2) { graphPanel.style.display = 'none'; return; }

        var dpr = window.devicePixelRatio || 1;
        var minT = times[0], maxT = times[times.length - 1];
        if (minT === maxT) maxT = minT + 1;

        // Build series for multi-component types
        var series = [];
        if (kind === 'coor') {
            var vx = [], vy = [];
            for (var i = 0; i < data.length; i++) { vx.push(data[i][0]); vy.push(data[i][1]); }
            series.push({values: vx, color: '#0ff', label: 'x'});
            series.push({values: vy, color: '#f80', label: 'y'});
        } else if (kind === 'tup' && data.length > 0 && Array.isArray(data[0]) && data[0].length > 1) {
            var nComp = data[0].length;
            var tColors = ['#0ff', '#f80', '#8f0', '#f0f'];
            var tLabels = ['a', 'b', 'c', 'd', 'e', 'f'];
            for (var c = 0; c < nComp; c++) {
                var vals = [];
                for (var i = 0; i < data.length; i++) vals.push(data[i][c]);
                series.push({values: vals, color: tColors[c % tColors.length], label: tLabels[c] || '' + c});
            }
        }

        if (series.length > 1) {
            drawAttrGraphStacked(msg, series, times, minT, maxT, dpr);
        } else {
            drawAttrGraphSingle(msg, times, data, kind, minT, maxT, dpr);
        }
    }

    // Inspect mode: toggle
    function toggleInspectMode() {
        inspectMode = !inspectMode;
        btnInspect.textContent = 'Inspect: ' + (inspectMode ? 'ON' : 'OFF');
        btnInspect.classList.toggle('active', inspectMode);
        if (inspectMode) {
            // Turn off conflicting modes
            if (measureMode) { measureMode = false; measurePoint1 = null; removeMeasureOverlay(); measureInfo.style.display = 'none'; }
            container.style.cursor = 'crosshair';
            showStatus('Inspect mode: hover to find, click to inspect');
        } else {
            container.style.cursor = '';
            removeHighlight();
            showStatus('Inspect mode off');
        }
    }
    btnInspect.addEventListener('click', toggleInspectMode);

    function highlightObject(idx) {
        removeHighlight();
        var info = objectsInfo[idx];
        if (!info || !info.bbox) return;
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        var ns = 'http://www.w3.org/2000/svg';
        var vb = currentViewbox || [0, 0, 1920, 1080];
        var sw = Math.min(vb[2], vb[3]) * 0.003;
        var pd = sw * 2;
        var rect = document.createElementNS(ns, 'rect');
        rect.setAttribute('id', '_highlight');
        rect.setAttribute('x', info.bbox[0] - pd);
        rect.setAttribute('y', info.bbox[1] - pd);
        rect.setAttribute('width', info.bbox[2] + pd * 2);
        rect.setAttribute('height', info.bbox[3] + pd * 2);
        rect.setAttribute('fill', 'none');
        rect.setAttribute('stroke', '#0ff');
        rect.setAttribute('stroke-width', sw);
        rect.setAttribute('stroke-dasharray', sw * 3 + ',' + sw * 2);
        rect.setAttribute('pointer-events', 'none');
        svgEl.appendChild(rect);
    }

    function removeHighlight() {
        var old = document.getElementById('_highlight');
        if (old) old.remove();
    }

    function closeInspect() {
        inspectPanel.style.display = 'none';
        graphPanel.style.display = 'none';
        inspectedIdx = -1;
        selectedAttr = '';
        lastGraphMsg = null;
        removeHighlight();
    }

    document.getElementById('inspect-close').addEventListener('click', closeInspect);

    // Click handler: measure tool, inspect mode, or default click-inspect
    container.addEventListener('click', function(e) {
        if (measureMode) {
            var svgEl = svgContent.querySelector('svg');
            if (!svgEl) return;
            var pt = clientToSvg(svgEl, e.clientX, e.clientY);
            if (!pt) return;
            if (!measurePoint1) {
                measurePoint1 = pt;
                showStatus('Measure: click second point');
                renderMeasureOverlay();
            } else {
                finishMeasure(pt);
            }
            return;
        }
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        var pt = clientToSvg(svgEl, e.clientX, e.clientY);
        if (!pt) return;

        if (inspectMode) {
            // In inspect mode: select nearest object
            var idx = findNearestObject(pt.x, pt.y);
            if (idx >= 0) { selectObject(idx); return; }
        } else {
            // Default: select object whose bbox contains click point
            var idx = findObjectAtPoint(pt.x, pt.y);
            if (idx >= 0) { selectObject(idx); return; }
        }
        // Clicked on empty space — close inspector
        if (inspectPanel.style.display === 'block') closeInspect();
    });

    document.addEventListener('keydown', function(e) {
        if (helpOverlay.classList.contains('visible')) {
            helpOverlay.classList.remove('visible');
            return;
        }
        const key = e.key.toUpperCase();
        if (key === 'Q') send({type: 'control', action: 'quit'});
        else if (key === 'R') send({type: 'control', action: 'restart'});
        else if (key === 'F' && !e.shiftKey && !e.ctrlKey) send({type: 'control', action: 'fit'});
        else if (key === 'S' && e.shiftKey) savePng();
        else if (key === 'S' && !e.shiftKey && !e.ctrlKey) saveSvg();
        else if (key === 'C' && !e.ctrlKey) copySvg();
        else if (key === 'P') togglePause();
        else if (key === ' ') { e.preventDefault(); togglePause(); }
        else if (e.key === ',' || e.key === '<') {
            send({type: 'control', action: 'step_backward'});
            showStatus('Step backward');
        }
        else if (e.key === '.' || e.key === '>') {
            send({type: 'control', action: 'step_forward'});
            showStatus('Step forward');
        }
        else if (e.key === 'ArrowRight') {
            e.preventDefault();
            send({type: 'control', action: 'next_section'});
        }
        else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            send({type: 'control', action: 'step_backward'});
            showStatus('Step backward');
        }
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            changeSpeed(0.25);
        }
        else if (e.key === 'ArrowDown') {
            e.preventDefault();
            changeSpeed(-0.25);
        }
        else if (e.key === 'Home') {
            e.preventDefault();
            send({type: 'control', action: 'jump_start'});
            showStatus('Jump to start');
        }
        else if (e.key === 'End') {
            e.preventDefault();
            send({type: 'control', action: 'jump_end'});
            showStatus('Jump to end');
        }
        else if (key === 'D') {
            debugVisible = !debugVisible;
            debugPanel.style.display = debugVisible ? 'block' : 'none';
            showStatus('Debug panel ' + (debugVisible ? 'ON' : 'OFF'));
        }
        else if (key === 'N') toggleSnap();
        else if (key === 'L') toggleLoop();
        else if (key === 'B' && !e.ctrlKey) cycleBg();
        else if (key === 'B' && e.ctrlKey) {
            e.preventDefault();
            toggleBookmark();
        }
        else if (e.key === '[') jumpToBookmark(-1);
        else if (e.key === ']') jumpToBookmark(1);
        else if (key === 'H') {
            document.body.classList.toggle('toolbars-hidden');
            showStatus('Toolbars ' + (document.body.classList.contains('toolbars-hidden') ? 'hidden' : 'visible'));
        }
        else if (key === 'G' && !e.ctrlKey) toggleGrid();
        else if (key === 'I' && !e.ctrlKey) {
            if (measureMode) { measureMode = false; measurePoint1 = null; removeMeasureOverlay(); measureInfo.style.display = 'none'; }
            toggleInspectMode();
        }
        else if (key === 'M' && !e.ctrlKey) {
            if (inspectMode) { inspectMode = false; btnInspect.textContent = 'Inspect: OFF'; btnInspect.classList.remove('active'); }
            measureMode = !measureMode;
            if (measureMode) {
                measurePoint1 = null;
                removeMeasureOverlay();
                measureInfo.style.display = 'none';
                showStatus('Measure: click first point');
                container.style.cursor = 'crosshair';
            } else {
                measurePoint1 = null;
                removeMeasureOverlay();
                measureInfo.style.display = 'none';
                container.style.cursor = '';
                showStatus('Measure off');
            }
        }
        else if (key === '-' || key === '_') changeSpeed(-0.25);
        else if (key === '=' || key === '+') changeSpeed(0.25);
        else if (e.key === '?') toggleHelp();
        else if (e.key === '0') {
            send({type: 'control', action: 'jump', percentage: 0});
            showStatus('Jump to 0%');
        }
        else if (e.key >= '1' && e.key <= '9') {
            var pct = parseInt(e.key) / 10;
            send({type: 'control', action: 'jump', percentage: pct});
            showStatus('Jump to ' + (pct * 100) + '%');
        }
    });

    container.addEventListener('wheel', function(e) {
        e.preventDefault();
        if (!currentViewbox) return;
        const factor = Math.pow(1.2, -e.deltaY / 240.0);
        const rect = container.getBoundingClientRect();
        const rel_x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const rel_y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
        send({type: 'zoom', factor: factor, rel_x: rel_x, rel_y: rel_y});
    }, {passive: false});

    container.addEventListener('mousemove', function(e) {
        if (!currentViewbox) return;
        const svgEl = svgContent.querySelector('svg');
        if (!svgEl) return;
        var pt = clientToSvg(svgEl, e.clientX, e.clientY);
        if (!pt) return;
        var vx = pt.x;
        var vy = pt.y;

        if (snapEnabled && snapPoints.length > 0) {
            var snap = findNearestSnap(svgEl, e.clientX, e.clientY);
            if (snap) {
                vx = snap.svgX;
                vy = snap.svgY;
                showSnapIndicator(snap.svgX, snap.svgY);
            } else {
                removeSnapIndicator();
            }
        } else {
            removeSnapIndicator();
        }

        coordsEl.textContent = 'x=' + vx.toFixed(2) + ' y=' + vy.toFixed(2);

        // Inspect mode: highlight nearest object on hover
        if (inspectMode && inspectedIdx < 0) {
            var hoverIdx = findNearestObject(pt.x, pt.y);
            if (hoverIdx >= 0) highlightObject(hoverIdx);
        }
    });

    connect();
})();
</script>
</body>
</html>
"""


class BrowserViewer:
    """Serves SVG frames to a browser via WebSocket.

    Handles the animation loop, WebSocket connections, optional hot-reload,
    speed control, and FPS tracking.
    """

    def __init__(self, canvas, fps: int = 60, port: int = 8765, hot_reload=False, script_path=None):
        self.canvas = canvas
        self.fps = fps
        self.port = port
        self.hot_reload = hot_reload
        self.script_path = script_path
        self.clients = set()
        self._loop = None
        self._anim_task = None
        self._watch_task = None
        self._server = None
        self._needs_rebroadcast = False

    def __repr__(self):
        return f'BrowserViewer(port={self.port}, fps={self.fps})'

    def _process_request(self, _connection, request):
        """Serve the HTML page for non-WebSocket HTTP requests."""
        if request.path == '/ws':
            return None  # Let websockets handle the upgrade
        return Response(
            200, 'OK',
            Headers([('Content-Type', 'text/html; charset=utf-8')]),
            _HTML_PAGE.encode(),
        )

    async def _handle_client(self, websocket):
        """Handle a single WebSocket client connection."""
        self.clients.add(websocket)
        self._needs_rebroadcast = True
        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                self.canvas.handle_browser_event(msg)
                self._needs_rebroadcast = True
        except websockets.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)

    async def _broadcast(self, data):
        """Send JSON data to all connected clients."""
        if not self.clients:
            return
        raw = json.dumps(data)
        await asyncio.gather(
            *(client.send(raw) for client in list(self.clients)),
            return_exceptions=True
        )

    async def _animation_loop(self):
        """Main animation loop: generates frames and broadcasts them.

        Respects single_picture mode (no time advancement) and
        speed_multiplier for variable playback speed.
        Only broadcasts when the frame has actually changed.
        """
        canvas = self.canvas
        dt = 1.0 / self.fps
        last_broadcast_time = None  # Track last broadcast canvas time
        last_broadcast_viewbox = None
        while True:
            t0 = time.monotonic()
            total = round((canvas.end_anim - canvas.start_anim) * self.fps) if canvas.end_anim else 0

            # Determine if we need to broadcast
            needs_broadcast = (last_broadcast_time != canvas.time
                               or last_broadcast_viewbox != canvas.viewbox
                               or self._needs_rebroadcast)

            if needs_broadcast:
                self._needs_rebroadcast = False
                svg = canvas.generate_frame_svg()

                frame_data = {
                    'type': 'frame',
                    'svg': svg,
                    'frame': canvas.frame_count,
                    'total_frames': total,
                    'time': canvas.time,
                    'start': canvas.start_anim,
                    'end': canvas.end_anim,
                    'viewbox': list(canvas.viewbox),
                    'speed': canvas.speed_multiplier,
                    'loop': canvas.loop_enabled,
                }
                if canvas.snap_enabled:
                    frame_data['snap_points'] = canvas.get_snap_points()
                else:
                    frame_data['snap_points'] = []
                frame_data['objects_info'] = canvas.get_visible_objects_info()
                await self._broadcast(frame_data)

                last_broadcast_time = canvas.time
                last_broadcast_viewbox = canvas.viewbox

            # Drain pending responses (inspect results, attribute graphs, etc.)
            while canvas._pending_responses:
                resp = canvas._pending_responses.pop(0)
                await self._broadcast(resp)

            # In single_picture mode, don't advance time
            if not canvas.single_picture and canvas.animate and canvas.frame_count < total:
                # Apply speed multiplier to time advancement
                advance = dt * canvas.speed_multiplier
                next_time = canvas.time + advance
                # Check if we've hit a section boundary
                for section_time in canvas.sections:
                    if canvas.time < section_time <= next_time:
                        canvas.time = section_time
                        canvas.frame_count = round((section_time - canvas.start_anim) * self.fps)
                        canvas.animate = False
                        await self._broadcast({'type': 'status', 'message': 'Section break \u2014 press Right Arrow'})
                        next_time = None
                        break
                if next_time is not None:
                    canvas.frame_count = round((next_time - canvas.start_anim) / dt)
                    canvas.time = min(next_time, canvas.end_anim)
            # Loop: restart when reaching the end
            elif (not canvas.single_picture and canvas.animate
                  and canvas.frame_count >= total and canvas.loop_enabled):
                canvas.time = canvas.start_anim
                canvas.frame_count = 0

            elapsed = time.monotonic() - t0
            await asyncio.sleep(max(0, dt - elapsed))

    async def _watch_script(self):
        """Poll the user's script for changes and re-execute on modification."""
        if not self.script_path or not os.path.isfile(self.script_path):
            return
        last_mtime = os.stat(self.script_path).st_mtime
        while True:
            await asyncio.sleep(0.5)
            try:
                mtime = os.stat(self.script_path).st_mtime
            except OSError:
                continue
            if mtime != last_mtime:
                last_mtime = mtime
                await self._broadcast({'type': 'status', 'message': 'Reloading...'})
                try:
                    with open(self.script_path, 'r') as f:
                        source = f.read()
                    code = compile(source, self.script_path, 'exec')
                    ns = {'__name__': '__main__', '__file__': self.script_path}
                    exec(code, ns)
                except Exception:
                    tb = traceback.format_exc()
                    logger.error('Hot-reload error:\n%s', tb)
                    await self._broadcast({'type': 'error', 'message': tb})

    def restart_animation(self):
        """Restart the animation loop (used after hot-reload)."""
        if self._anim_task:
            self._anim_task.cancel()
        if self._loop is None:
            raise RuntimeError('Event loop not initialized')
        self._anim_task = self._loop.create_task(self._animation_loop())

    def start(self):
        """Start the server and animation loop (blocking)."""
        global _active_viewer

        if _active_viewer is not None and _active_viewer._server is not None:
            # Hot-reload: reuse existing server, just restart animation
            _active_viewer.canvas = self.canvas
            _active_viewer.fps = self.fps
            _active_viewer.restart_animation()
            return

        _active_viewer = self
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        async def _run():
            self._server = await websockets.serve(
                self._handle_client,
                'localhost',
                self.port,
                process_request=self._process_request,
            )
            logger.info('VectorMation browser viewer at http://localhost:%d', self.port)
            # Wait briefly for existing tab reconnection before opening a new one
            for _ in range(10):
                await asyncio.sleep(0.3)
                if self.clients:
                    break
            if not self.clients:
                webbrowser.open(f'http://localhost:{self.port}')
            self._anim_task = asyncio.ensure_future(self._animation_loop())
            if self.hot_reload and self.script_path:
                self._watch_task = asyncio.ensure_future(self._watch_script())
            await asyncio.Future()  # Run forever

        try:
            self._loop.run_until_complete(_run())
        except KeyboardInterrupt:
            logger.info('Shutting down...')
        finally:
            for task in asyncio.all_tasks(self._loop):
                task.cancel()
            self._loop.run_until_complete(
                asyncio.gather(*asyncio.all_tasks(self._loop), return_exceptions=True)
            )
            _active_viewer = None
            self._loop.close()
