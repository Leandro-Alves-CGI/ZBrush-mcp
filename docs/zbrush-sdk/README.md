# ZBrush SDK – Espelho no repositório

Este diretório guarda um **espelho em Markdown** de páginas públicas do SDK do ZBrush/Maxon.
Ele é atualizado automaticamente por um workflow do GitHub Actions.

## O que tem aqui
- `index.md`: índice com links para as páginas espelhadas.
- `pages/`: os arquivos `.md` de cada página coletada.
- `changes/`: log com o que mudou a cada execução (um arquivo por data).
- `sources.txt`: a lista de URLs oficiais para coletar (uma por linha).

## Como funciona
1. Você edita `sources.txt` com as páginas que deseja espelhar.
2. O GitHub Actions roda o script `tools/zbrush_sdk_scrape.py`, baixa o conteúdo permitido,
   converte para Markdown e salva em `pages/`.
3. Se houver mudanças, o workflow **comita** os arquivos neste diretório automaticamente.

> Importante: o script respeita `robots.txt`. Se um site bloquear scraping,
> a página será ignorada.
