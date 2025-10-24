#!/usr/bin/env python3
# ZBrush-mcp – Doc Mirror (versão permissiva, sem bloquear por robots)
# Observação: antes de usar em produção, confira os termos de uso das páginas.
# Este script cria/atualiza Markdown em docs/zbrush-sdk/pages/ a partir das URLs do sources.txt.

import os, re, sys, time, difflib, datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]        # raiz do repo
DOCS = ROOT / "docs" / "zbrush-sdk"
PAGES = DOCS / "pages"
CHANGES = DOCS / "changes"
SOURCES = DOCS / "sources.txt"

USER_AGENT = "Mozilla/5.0 (compatible; ZBrush-mcp-DocMirror/1.0)"

def log(msg: str):
    print(msg, flush=True)

def load_sources():
    if not SOURCES.exists():
        log("[WARN] sources.txt não encontrado.")
        return []
    urls = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls

def fetch(url):
    """Baixa a URL e retorna (content, content_type). Lança exceção em erro HTTP."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    r = requests.get(url, headers=headers, timeout=45)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "").lower()
    return r.content, ctype

def html_to_md(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove elementos de navegação comuns para limpar o texto
    for sel in ["nav", "header", "footer", "script", "style", "noscript"]:
        for tag in soup.select(sel):
            tag.decompose()

    # Tenta usar o <main> se existir (conteúdo principal)
    main = soup.find("main")
    container = main if main else soup

    title = container.title.get_text(strip=True) if container.title else (soup.title.get_text(strip=True) if soup.title else base_url)
    # Texto com quebras razoáveis
    body = container.get_text("\n", strip=True)
    body = re.sub(r"\n{3,}", "\n\n", body)

    md = f"# {title}\n\nFonte: {base_url}\n\n---\n\n{body}\n"
    return md

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "pagina"

def target_path(url: str, md_title: str) -> Path:
    host = urlparse(url).netloc.replace(".", "-")
    slug = slugify(md_title)[:80]
    return PAGES / f"{host}-{slug}.md"

def write_if_changed(path: Path, new_text: str):
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == new_text:
        return None  # sem mudança
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_text, encoding="utf-8")

    diff = difflib.unified_diff(
        old.splitlines(), new_text.splitlines(),
        fromfile="old", tofile="new", lineterm="", n=3
    )
    return "\n".join(list(diff)[:2000])  # limita o tamanho do diff

def make_markdown_from_pdf(url: str) -> str:
    # Para PDFs, criamos um MD simples com o link (não baixamos o binário)
    title = "Documento PDF"
    md = f"# {title}\n\nFonte (PDF): {url}\n\n---\n\nEste item é um PDF. Acesse o link acima para visualizar.\n"
    return md, title

def process_url(url: str):
    """Processa uma única URL: gera Markdown e retorna (path, diff or None)."""
    log(f"[FETCH] {url}")
    content, ctype = fetch(url)

    if "pdf" in ctype or url.lower().endswith(".pdf"):
        md, title = make_markdown_from_pdf(url)
    else:
        # Assume HTML / texto
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = content.decode("latin-1", errors="ignore")
        md = html_to_md(text, url)
        # extrai título para nome do arquivo
        m = re.search(r"^#\s+(.+)$", md, flags=re.MULTILINE)
        title = m.group(1).strip() if m else url

    path = target_path(url, title)
    diff = write_if_changed(path, md)
    if diff:
        log(f"[UPDATED] {path}")
    else:
        log(f"[NO CHANGE] {path}")
    return path, diff

def update_index():
    items = []
    for p in sorted(PAGES.glob("*.md")):
        try:
            first = p.read_text(encoding="utf-8").splitlines()[0]
            title = first.lstrip("# ").strip() if first.startswith("#") else p.stem
        except Exception:
            title = p.stem
        rel = p.relative_to(DOCS).as_posix()
        items.append(f"- [{title}](/{rel})")
    index = "# ZBrush SDK – Índice\n\n" + ("\n".join(items) if items else "(Sem páginas ainda. Verifique o sources.txt e rode o workflow.)") + "\n"
    (DOCS / "index.md").write_text(index, encoding="utf-8")

def main():
    today = datetime.date.today().isoformat()
    CHANGES.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)

    urls = load_sources()
    if not urls:
        log("sources.txt vazio. Nada a fazer.")
        # ainda atualiza o índice vazio
        update_index()
        return

    changed = []
    for url in urls:
        try:
            path, diff = process_url(url)
            if diff:
                changed.append((url, path, diff))
            time.sleep(1.0)  # cortesia
        except requests.HTTPError as e:
            log(f"[ERRO HTTP] {url} -> {e}")
        except Exception as e:
            log(f"[ERRO] {url} -> {e}")

    # Atualiza índice
    update_index()

    # Changelog do dia (apenas se houve mudanças)
    if changed:
        lines = [f"# Mudanças em {today}\n"]
        for url, path, diff in changed:
            rel = path.relative_to(DOCS).as_posix()
            lines.append(f"## {url}\nArquivo: `/{rel}`\n\n```diff\n{diff}\n```\n")
        (CHANGES / f"{today}.md").write_text("\n".join(lines), encoding="utf-8")
        log(f"[RESUMO] {len(changed)} página(s) atualizada(s).")
    else:
        log("[RESUMO] Nenhuma mudança detectada.")

if __name__ == "__main__":
    main()
