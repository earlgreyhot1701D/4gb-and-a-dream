"""Record the 4 GB and a Dream tour from the repo files.

Serves the repos locally, routes the CDN and Google Fonts requests to local
copies (this workspace can't reach them), drives each round, and writes an MP4.
"""
import asyncio, pathlib, shutil, subprocess, threading, http.server, socketserver, functools
from playwright.async_api import async_playwright

ROOT = pathlib.Path("/home/claude/demo/site")
PORT = 8765
BASE = f"http://localhost:{PORT}"
W, H = 1280, 720

FONT_CSS = f"""
@font-face{{font-family:Fraunces;font-weight:700;src:url({BASE}/fonts/fraunces/files/fraunces-latin-700-normal.woff2)}}
@font-face{{font-family:Fraunces;font-weight:900;src:url({BASE}/fonts/fraunces/files/fraunces-latin-900-normal.woff2)}}
@font-face{{font-family:Nunito;font-weight:700;src:url({BASE}/fonts/nunito/files/nunito-latin-700-normal.woff2)}}
@font-face{{font-family:Nunito;font-weight:800;src:url({BASE}/fonts/nunito/files/nunito-latin-800-normal.woff2)}}
@font-face{{font-family:Cinzel;font-weight:600;src:url({BASE}/fonts/cinzel/files/cinzel-latin-600-normal.woff2)}}
@font-face{{font-family:Cinzel;font-weight:700;src:url({BASE}/fonts/cinzel/files/cinzel-latin-700-normal.woff2)}}
@font-face{{font-family:"Source Serif 4";font-weight:400;src:url({BASE}/fonts/source-serif-4/files/source-serif-4-latin-400-normal.woff2)}}
@font-face{{font-family:"Source Serif 4";font-weight:600;src:url({BASE}/fonts/source-serif-4/files/source-serif-4-latin-600-normal.woff2)}}
@font-face{{font-family:"JetBrains Mono";font-weight:500;src:url({BASE}/fonts/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2)}}
@font-face{{font-family:"JetBrains Mono";font-weight:600;src:url({BASE}/fonts/jetbrains-mono/files/jetbrains-mono-latin-600-normal.woff2)}}
"""

# A visible cursor and a lower-third label, so viewers can follow along.
OVERLAY_JS = r"""
(() => {
  if (window.__demoOverlay) return; window.__demoOverlay = true;
  const add = () => {
    const c = document.createElement('div');
    c.id = '__cursor';
    c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,0.85);border:2px solid #0A1F2E;box-shadow:0 0 0 4px rgba(31,181,183,0.45);z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:transform .12s';
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    document.addEventListener('mousedown', () => { c.style.transform = 'translate(-50%,-50%) scale(0.75)'; }, true);
    document.addEventListener('mouseup', () => { c.style.transform = 'translate(-50%,-50%)'; }, true);
    const l = document.createElement('div');
    l.id = '__label';
    l.style.cssText = 'position:fixed;left:24px;bottom:22px;z-index:99998;pointer-events:none;background:rgba(10,31,46,0.92);color:#E8E0CC;border-left:4px solid #1FB5B7;padding:10px 16px;border-radius:6px;font:600 15px "JetBrains Mono",monospace;letter-spacing:.08em;text-transform:uppercase;box-shadow:0 6px 18px rgba(0,0,0,.25)';
    l.textContent = window.__labelText || '';
    if (!l.textContent) l.style.display = 'none';
    document.body.appendChild(l);
    const st = document.createElement('style'); st.textContent = '.meter{display:none!important}'; document.head.appendChild(st);
  };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
})();
"""

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def serve():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

async def label(page, text):
    await page.evaluate("t => { window.__labelText = t; const l = document.getElementById('__label'); if (l) { l.textContent = t; l.style.display = t ? 'block' : 'none'; } }", text)

async def glide(page, x0, y0, x1, y1, steps=25):
    await page.mouse.move(x0, y0)
    await page.mouse.move(x1, y1, steps=steps)

async def click_el(page, selector, pause=900):
    loc = page.locator(selector).first
    box = await loc.bounding_box()
    await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=18)
    await page.wait_for_timeout(250)
    box = await loc.bounding_box()  # re-measure: the page may have scrolled while the cursor moved
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    await page.mouse.move(x, y, steps=4)
    await page.mouse.down(); await page.wait_for_timeout(120); await page.mouse.up()
    await page.wait_for_timeout(pause)

async def goto(page, url, text):
    await page.goto(url, wait_until="load")
    await page.wait_for_timeout(300)
    await label(page, text)

async def main():
    httpd = serve()
    raw = pathlib.Path("/home/claude/demo/raw"); shutil.rmtree(raw, ignore_errors=True); raw.mkdir()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True,
                                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(raw),
                                        record_video_size={"width": W, "height": H})
        await ctx.route("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
                        lambda r: r.fulfill(path=str(ROOT / "three/three.min.js"), content_type="application/javascript"))
        await ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(body=FONT_CSS, content_type="text/css"))
        await ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        await ctx.add_init_script(OVERLAY_JS)
        page = await ctx.new_page()

        # 1. Landing
        await goto(page, f"{BASE}/4gb/", "4 GB and a Dream · built from a 4 GB Chromebook")
        await page.mouse.move(640, 300)
        await page.wait_for_timeout(2600)

        # 2. Round 1: Necesito (demo number, not a real one)
        await goto(page, f"{BASE}/necesito/#5551234567", "§ 01 · Necesito · a live app, no editor")
        await page.evaluate("document.addEventListener('click', e => { const a = e.target.closest('a[href^=\"sms:\"]'); if (a) e.preventDefault(); }, true)")
        await page.wait_for_timeout(1400)
        await click_el(page, "a.btn.pink", 700)      # Té, por favor (press animation; Messages can't be filmed)
        await click_el(page, "a.btn.yellow", 700)    # Ven a sentarte conmigo
        await page.mouse.wheel(0, 260); await page.wait_for_timeout(1300)
        await page.mouse.wheel(0, -260); await page.wait_for_timeout(600)

        # 3. Round 2: 3D flags
        await goto(page, f"{BASE}/4gb/round-2-3d/", "§ 02 · Papel picado in 3D · drawn by your device")
        await page.wait_for_timeout(2200)
        await page.mouse.move(560, 380, steps=15)
        await page.mouse.down()
        await page.mouse.move(760, 370, steps=30)
        await page.mouse.up()
        await page.wait_for_timeout(600)
        for _ in range(2):
            await page.mouse.wheel(0, -120); await page.wait_for_timeout(150)
        await page.wait_for_timeout(1600)

        # 4. Round 3: the bootstrapping path
        await goto(page, f"{BASE}/4gb/round-3-diagram/", "§ 03 · The bootstrapping path · follow the thread")
        await page.wait_for_timeout(1500)
        await click_el(page, "#next", 2300)   # first click stops autoplay and steps forward
        await click_el(page, "#next", 2300)
        await click_el(page, "#next", 2300)
        await click_el(page, "#wifi", 2800)   # What if the Wi-Fi drops?
        await click_el(page, "#next", 2300)
        await click_el(page, "#wifi", 2600)   # Bring the Wi-Fi back

        # 5. Back to the landing page
        await goto(page, f"{BASE}/4gb/", "Every build: Chromebook + Claude + GitHub · no IDE")
        await page.mouse.move(640, 320)
        await page.wait_for_timeout(3200)

        video = page.video
        await ctx.close(); await browser.close()
    httpd.shutdown()
    return pathlib.Path(await video.path())

if __name__ == "__main__":
    raw = asyncio.run(main())
    out = "/home/claude/demo/4gb-tour.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-an", out], check=True)
    print("SUCCESS", out)
