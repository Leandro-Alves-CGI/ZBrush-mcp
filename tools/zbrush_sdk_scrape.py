#!/usr/bin/env python3
import hashlib, os, time, re, sys, difflib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import datetime
import urllib.robotparser as robotparser

ROOT = Path(__file__).resolve().parents[1]  # repo root
DOCS = ROOT / "docs" / "zbrush-sdk"
PAGES = DOCS / "pages"
CHANGES = DOCS / "changes"
SOURCES = DOCS / "sources.txt"
USER_AGENT = "ZBrush-mcp-DocMirror/1.0"

def load_sources():
    if not SOURCES.exists():
        return []
    urls = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls

def allowed(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # Se não conseguir ler robots.txt, seja conservador
        return False

def fetch(url):
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def html_to_md(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    # Remove navegação/cabeçalho/rodapé/scripts/estilos
    for sel in ["nav", "header", "footer", "script", "style"]:
        for tag in soup.select(sel):
            tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else base_url
    body = soup.get_text("\n", strip=True)

    # Compacta quebras repetidas
    body = re.sub(r"\n{3,}", "\n\n", body)

    md = f"# {title}\n\nFonte: {base_url}\n\n---\n\n{body}\n"
    return md

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "pagina"

def target_path(url, md):
    host = urlparse(url).netloc.replace(".", "-")
    m = re.search(r"^#\s+(.+)$", md, flags=re.MULTILINE)
    title = m.group(1) if m else url
    slug = slugify(title)[:80]
    return PAGES / f"{host}-{slug}.md"

def write_if_changed(path, new_text):
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == new_text:
        return None  # sem mudanças
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_text, encoding="utf-8")
    diff = difflib.unified_diff(
        old.splitlines(), new_text.splitlines(),
        lineterm="", n=3, fromfile="old", tofile="new"
    )
    return "\n".join(list(diff)[:2000])  # limita tamanho

def main():
    today = datetime.date.today().isoformat()
    CHANGES.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    changed = []

    urls = load_sources()
    if not urls:
        print("sources.txt vazio ou ausente.")
        sys.exit(0)

    for url in urls:
        if not allowed(url):
            print(f"[SKIP robots] {url}")
            continue
        try:
            html = fetch(url)
            md = html_to_md(html, url)
            path = target_path(url, md)
            diff = write_if_changed(path, md)
            if diff:
                changed.append((url, path, diff))
            time.sleep(1.0)  # cortesia
        except Exception as e:
            print(f"[ERRO] {url}: {e}", file=sys.stderr)

    if changed:
        # Atualiza index e changelog
        index = ["# ZBrush SDK – Índice\n"]
        for p in sorted(PAGES.glob("*.md")):
            rel = p.relative_to(DOCS).as_posix()
            try:
                title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            except Exception:
                title = p.name
            index.append(f"- [{title}](/{rel})")
        (DOCS / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

        log = [f"# Mudanças em {today}\n"]
        for url, path, diff in changed:
            rel = path.relative_to(DOCS).as_posix()
            log.append(f"## {url}\nArquivo: `/{rel}`\n\n```diff\n{diff}\n```\n")
        (CHANGES / f"{today}.md").write_text("\n".join(log) + "\n", encoding="utf-8")

        print(f"{len(changed)} página(s) atualizada(s).")
    else:
        print("Nenhuma mudança detectada.")

if __name__ == "__main__":
    main()
