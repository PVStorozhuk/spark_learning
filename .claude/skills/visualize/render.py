"""Render a Mermaid or SVG source file to PNG for the visualize skill.

Replaces the render_mermaid / render_svg tools of the upstream pi `visual-tools` extension.

Usage (from the project root):
    python .claude/skills/visualize/render.py mermaid <source.mmd>                 # preview
    python .claude/skills/visualize/render.py svg <source.svg>                     # preview
    python .claude/skills/visualize/render.py mermaid <source.mmd> --publish <slug>

Preview writes <viz>/.preview/<source-stem>-<time>-<pid>.png, a fresh file per render, so makers
running in parallel never see each other's pictures. Publish writes <viz>/viz-<slug>-<timestamp>.png
and never overwrites an existing file. <viz> is notes/viz, or <dir>/viz when the session log
(notes/sessions/.config) points at another directory, so embeds resolve inside the same vault.
Prints `filename:` and `path:` lines on success; exits non-zero with the renderer's error otherwise.

Mermaid uses `npx @mermaid-js/mermaid-cli` (the first run downloads it and a headless browser,
which can take a few minutes). SVG uses rsvg-convert when available, otherwise a headless
Chromium browser (Edge or Chrome).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[3]))
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.17.0"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
DIMENSION = r"""(?<![\w-]){name}\s*=\s*["']\s*([\d.]+)\s*(?:px)?\s*["']"""
VIEW_BOX = r"""viewBox\s*=\s*["']\s*[\d.\-]+[\s,]+[\d.\-]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*["']"""


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def viz_dir() -> Path:
    config = ROOT / "notes" / "sessions" / ".config"
    value = config.read_text(encoding="utf-8").strip().strip('"') if config.is_file() else ""
    if value and value not in ("on", "off"):
        target = Path(value)
        return (target if target.is_absolute() else ROOT / target) / "viz"
    return ROOT / "notes" / "viz"


def run(cmd: list, timeout: int) -> None:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # npx is a .cmd shim on Windows: kill the whole tree (cmd -> node -> browser), not just the shim.
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            proc.kill()
        proc.communicate()
        fail(f"renderer timed out after {timeout}s: {cmd[0]}")
    if proc.returncode != 0:
        fail((stderr or stdout).strip()[-2000:] or f"renderer exited with {proc.returncode}")


def render_mermaid(src: Path, out: Path) -> None:
    npx = shutil.which("npx")
    if not npx:
        fail("npx not found; install Node.js")
    run([npx, "-y", MERMAID_CLI, "-i", str(src), "-o", str(out), "-b", "white", "-s", "2", "-q"], timeout=600)


def svg_size(text: str) -> tuple:
    root = re.search(r"<svg\b[^>]*>", text, re.S)
    if not root:
        fail("no <svg> root element found")
    tag = root.group(0)
    # The lookbehind keeps "width" from matching inside "stroke-width"; only plain or px values count.
    width = re.search(DIMENSION.format(name="width"), tag)
    height = re.search(DIMENSION.format(name="height"), tag)
    if width and height:
        return int(float(width.group(1))), int(float(height.group(1)))
    view_box = re.search(VIEW_BOX, tag)
    if view_box:
        return int(float(view_box.group(1))), int(float(view_box.group(2)))
    fail("the <svg> element needs a numeric width/height or a viewBox")


def render_svg(src: Path, out: Path) -> None:
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        run([rsvg, "-z", "2", "-b", "white", "-o", str(out), str(src)], timeout=60)
        return
    browser = next((b for b in BROWSERS if Path(b).exists()), None) or shutil.which("chromium")
    if not browser:
        fail("no SVG renderer found (rsvg-convert, Edge, Chrome, or Chromium)")
    width, height = svg_size(src.read_text(encoding="utf-8"))
    run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
         f"--window-size={width},{height}", f"--screenshot={out}", src.resolve().as_uri()], timeout=120)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["mermaid", "svg"])
    parser.add_argument("source", type=Path)
    parser.add_argument("--publish", metavar="SLUG", help="publish with a unique filename for embedding")
    args = parser.parse_args()

    if not args.source.is_file():
        fail(f"source file not found: {args.source}")
    viz = viz_dir()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    if args.publish:
        slug = re.sub(r"[^a-z0-9]+", "-", args.publish.lower()).strip("-") or "diagram"
        out = viz / f"viz-{slug}-{stamp}.png"
        if out.exists():
            fail(f"refusing to overwrite {out}; publish again")
    else:
        stem = re.sub(r"[^A-Za-z0-9_-]+", "-", args.source.stem)
        out = viz / ".preview" / f"{stem}-{stamp}-{os.getpid()}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    (render_mermaid if args.kind == "mermaid" else render_svg)(args.source, out)
    if not out.is_file() or out.stat().st_size == 0:
        fail("renderer reported success but wrote no PNG")
    print(f"filename: {out.name}")
    print(f"path: {out}")


if __name__ == "__main__":
    main()
