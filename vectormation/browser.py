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
#toolbar, #toolbar2 {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 10px; background: #2d2d2d; border-bottom: 1px solid #444;
    flex-shrink: 0; font-size: 13px;
}
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
#btn-snap.active { background: #0078d4; color: #fff; border-color: #0078d4; }
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
    padding: 20px 28px; max-width: 420px; width: 90%;
    color: #ccc; font-family: monospace; font-size: 13px;
}
#help-box h3 { color: #8cf; margin: 0 0 12px 0; font-size: 15px; }
#help-box table { width: 100%; border-collapse: collapse; }
#help-box td { padding: 3px 0; }
#help-box td:first-child { color: #ff0; width: 110px; }
#help-box .help-close {
    display: block; text-align: center; margin-top: 14px;
    color: #888; font-size: 12px;
}
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
    <button id="btn-save" title="Save SVG (S)">Save SVG</button>
    <span style="flex:1"></span>
    <button id="btn-help" title="Keyboard Shortcuts (?)">?</button>
</div>
<div id="svg-container">
    <div id="svg-content"></div>
</div>
<div id="status"></div>
<div id="error-box"></div>
<div id="help-overlay">
<div id="help-box">
    <h3>Keyboard Shortcuts</h3>
    <table>
    <tr><td>Space / P</td><td>Pause / Resume</td></tr>
    <tr><td>R</td><td>Restart</td></tr>
    <tr><td>, / .</td><td>Step backward / forward</td></tr>
    <tr><td>&larr; / &rarr;</td><td>Prev section / Next section</td></tr>
    <tr><td>- / +</td><td>Slower / Faster</td></tr>
    <tr><td>1 &ndash; 9</td><td>Jump to 10% &ndash; 90%</td></tr>
    <tr><td>F</td><td>Reset zoom</td></tr>
    <tr><td>S</td><td>Save SVG</td></tr>
    <tr><td>N</td><td>Toggle snap</td></tr>
    <tr><td>D</td><td>Debug panel</td></tr>
    <tr><td>Q</td><td>Quit</td></tr>
    </table>
    <span class="help-close">Press any key or click to close</span>
</div>
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
    let ws = null;
    let paused = false;
    let currentViewbox = null;
    let statusTimeout = null;
    let currentSpeed = 1.0;
    let currentEndTime = 0;
    let snapEnabled = false;
    let snapPoints = [];
    let debugVisible = false;
    const btnSnap = document.getElementById('btn-snap');
    const SNAP_THRESHOLD_PX = 15;

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
                currentEndTime = endT;
                var duration = endT - (msg.start !== undefined ? msg.start : 0);
                var pct = duration > 0 ? ((t - (msg.start || 0)) / duration * 100) : 100;
                progressBar.style.width = Math.min(100, Math.max(0, pct)) + '%';
                progressText.textContent = t.toFixed(2) + 's / ' + endT.toFixed(2) + 's';
                if (msg.speed !== undefined) currentSpeed = msg.speed;
                speedInfo.textContent = currentSpeed.toFixed(1) + 'x';
                if (msg.snap_points !== undefined) snapPoints = msg.snap_points;
                if (debugVisible) {
                    debugTime.textContent = 'Time: ' + t.toFixed(3) + 's';
                    debugFrame.textContent = 'Frame: ' + (msg.frame || 0) + ' / ' + (msg.total_frames || 0);
                    if (msg.objects_info) {
                        debugObjects.innerHTML = msg.objects_info.map(function(o) {
                            return '<div class="obj-item">' + o['class'] + '</div>';
                        }).join('');
                    }
                }
            } else if (msg.type === 'status') {
                showStatus(msg.message);
            } else if (msg.type === 'error') {
                showError(msg.message);
            }
        };
        ws.onclose = function() {
            showStatus('Disconnected \u2014 reconnecting...');
            setTimeout(connect, 1000);
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
    }

    function changeSpeed(delta) {
        currentSpeed = Math.max(0.1, Math.round((currentSpeed + delta) * 10) / 10);
        send({type: 'control', action: 'speed', value: currentSpeed});
        showStatus('Speed: ' + currentSpeed.toFixed(1) + 'x');
    }

    // Click on progress bar to seek to a specific time
    progressWrap.addEventListener('click', function(e) {
        var rect = progressWrap.getBoundingClientRect();
        var pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        send({type: 'control', action: 'jump', percentage: pct});
        showStatus('Jump to t=' + (pct * currentEndTime).toFixed(2) + 's');
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
    document.getElementById('btn-save').addEventListener('click', saveSvg);
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

    function removeSnapIndicator() {
        var old = document.getElementById('_snap_ind');
        if (old) old.remove();
    }

    function showSnapIndicator(svgX, svgY) {
        removeSnapIndicator();
        var svgEl = svgContent.querySelector('svg');
        if (!svgEl || !currentViewbox) return;
        var vb = currentViewbox;
        // Size the crosshair relative to the viewbox so it looks consistent at any zoom
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

    document.addEventListener('keydown', function(e) {
        if (helpOverlay.classList.contains('visible')) {
            helpOverlay.classList.remove('visible');
            return;
        }
        const key = e.key.toUpperCase();
        if (key === 'Q') send({type: 'control', action: 'quit'});
        else if (key === 'R') send({type: 'control', action: 'restart'});
        else if (key === 'F') send({type: 'control', action: 'fit'});
        else if (key === 'S') saveSvg();
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
        else if (key === 'D') {
            debugVisible = !debugVisible;
            debugPanel.style.display = debugVisible ? 'block' : 'none';
            showStatus('Debug panel ' + (debugVisible ? 'ON' : 'OFF'));
        }
        else if (key === 'N') toggleSnap();
        else if (key === '-' || key === '_') changeSpeed(-0.25);
        else if (key === '=' || key === '+') changeSpeed(0.25);
        else if (e.key === '?') toggleHelp();
        // Number keys 1-9: jump to that percentage of the animation
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

    def __init__(self, canvas, fps=60, port=8765, hot_reload=False, script_path=None):
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

    def _process_request(self, connection, request):
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
                }
                if canvas.snap_enabled:
                    frame_data['snap_points'] = canvas.get_snap_points()
                else:
                    frame_data['snap_points'] = []
                frame_data['objects_info'] = canvas.get_visible_objects_info()
                await self._broadcast(frame_data)

                last_broadcast_time = canvas.time
                last_broadcast_viewbox = canvas.viewbox

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
        assert self._loop is not None
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
            print(f'VectorMation browser viewer at http://localhost:{self.port}')
            # Wait briefly for existing tab reconnection
            await asyncio.sleep(1.5)
            if not self.clients:
                webbrowser.open(f'http://localhost:{self.port}')
            self._anim_task = asyncio.ensure_future(self._animation_loop())
            if self.hot_reload and self.script_path:
                self._watch_task = asyncio.ensure_future(self._watch_script())
            await asyncio.Future()  # Run forever

        try:
            self._loop.run_until_complete(_run())
        except KeyboardInterrupt:
            print('\nShutting down...')
        finally:
            for task in asyncio.all_tasks(self._loop):
                task.cancel()
            self._loop.run_until_complete(
                asyncio.gather(*asyncio.all_tasks(self._loop), return_exceptions=True)
            )
            _active_viewer = None
            self._loop.close()
