#!/usr/bin/env python3
"""CILRAP and FICHL bounded public-site adapter for CILRAPSearcher."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from skillkit import HTTP, RetrievalError, clean, matches, pdf_pages, result, snippet, terms

PROG = "cilrap_search.py"
DESCRIPTION = "Search the public CILRAP site and its FICHL section by bounded crawl."
CACHE_DEFAULT = ".cilrap-cache"
FETCH_TIMEOUT_DEFAULT = 300

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/155.0.0.0 Safari/537.36"
)
SEEDS = {
    "cilrap": [
        "https://www.cilrap.org/purpose",
        "https://www.cilrap.org/thematic-libraries",
        "https://www.cilrap.org/events",
        "https://www.cilrap.org/news",
    ],
    "fichl": ["https://www.cilrap.org/fichl"],
}
PATHS = {"cilrap": ["/"], "fichl": ["/fichl"]}


def _headers() -> dict[str, str]:
    return {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def make_http(args: argparse.Namespace) -> HTTP:
    return HTTP(
        args.cache,
        offline=args.offline,
        ttl=args.cache_ttl,
        timeout=args.timeout,
        user_agent=UA,
    )


def add_search_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=("cilrap", "fichl", "all"), default="all")
    parser.add_argument("--limit", type=int, default=10, help="1..50 (default 10)")
    parser.add_argument("--offset", type=int, default=0, help=">= 0 (default 0)")
    parser.add_argument("--max-pages", type=int, default=12, help="Pages per scope (1..2000)")
    parser.add_argument("--depth", type=int, default=1, help="Link depth (0..5)")


def add_fetch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text-out", help="Write extracted page text here")
    parser.add_argument("--pdf-out", help="Write a PDF response here")
    parser.add_argument("--max-mb", type=int, default=250, help="Maximum response size in MiB")


def _allowed(url: str, scope: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or (parsed.hostname or "").lower() != "www.cilrap.org":
        return False
    if re.search(r"\.(png|jpg|gif|mp4|mp3|zip|css|js)$", parsed.path, re.I):
        return False
    return any(parsed.path.startswith(prefix) for prefix in PATHS[scope])


def _crawl_scope(http: HTTP, scope: str, query: str, limit: int, offset: int, max_pages: int, depth: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    queue = [(url, 0, "") for url in SEEDS[scope]]
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    fetched = 0
    while queue and fetched < max_pages:
        url, current_depth, label = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        fetched += 1
        try:
            body, meta = http.get(url, headers=_headers())
            if body.startswith(b"%PDF"):
                for page in pdf_pages(body):
                    text = page["text"]
                    if matches(query, text):
                        rows.append(
                            result(
                                label or url,
                                meta["source_url"] + "#page=" + str(page["page"]),
                                "http-pdf",
                                snippet(text, query),
                                page=page["page"],
                                scope=scope,
                                access="PDF page text; bounded crawl",
                            )
                        )
                continue
            soup = BeautifulSoup(body, "html.parser")
            title = clean(soup.title.get_text(" ", strip=True) if soup.title else label or url)
            content = soup.select_one("main") or soup.select_one("article") or soup.body or soup
            text = content.get_text(" ", strip=True)
            if matches(query, text):
                rows.append(
                    result(
                        title,
                        meta["source_url"],
                        "http-local-text",
                        snippet(text, query),
                        scope=scope,
                        access="page text; bounded crawl",
                    )
                )
            for anchor in content.select("a[href]"):
                target = urljoin(meta["source_url"], anchor["href"]).split("#")[0]
                anchor_text = clean(anchor.get_text(" ", strip=True))
                if not _allowed(target, scope):
                    continue
                if anchor_text and matches(query, anchor_text):
                    rows.append(
                        result(
                            anchor_text,
                            target,
                            "http-catalogue-link",
                            anchor_text,
                            scope=scope,
                            discovered_on=meta["source_url"],
                            access="link-label-only; target not fetched",
                        )
                    )
                if current_depth < depth and target not in seen:
                    queue.append((target, current_depth + 1, anchor_text))
            queue.sort(
                key=lambda item: (
                    item[1],
                    -sum(term in item[2].casefold() for term in terms(query)),
                )
            )
        except (RetrievalError, ValueError) as exc:
            errors.append(str(exc))
    return rows, {
        "scope": scope,
        "pages_attempted": fetched,
        "queued_unvisited": len(queue),
        "matched_in_visited_pages": len(rows),
        "errors": errors,
        "exhaustive": False,
    }


def search(query: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("A non-empty query is required")
    if not 1 <= args.limit <= 50:
        raise ValueError("limit must be 1..50")
    if args.offset < 0:
        raise ValueError("offset must be >= 0")
    if not 1 <= args.max_pages <= 2000 or not 0 <= args.depth <= 5:
        raise ValueError("max-pages must be 1..2000 and depth 0..5")
    scopes = ("cilrap", "fichl") if args.scope == "all" else (args.scope,)
    all_rows: list[dict[str, Any]] = []
    reports = []
    for scope in scopes:
        rows, info = _crawl_scope(http, scope, query, args.limit, args.offset, args.max_pages, args.depth)
        all_rows.extend(rows)
        reports.append(info)
    unique: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        unique.setdefault(row["url"], row)
    rows = list(unique.values())
    selected = rows[args.offset : args.offset + args.limit]
    warnings = [error for report in reports for error in report["errors"]]
    return {
        "status": "partial",
        "query": query,
        "total": len(rows),
        "results": selected,
        "pagination": {
            "offset": args.offset,
            "limit": args.limit,
            "next_offset": args.offset + len(selected) if args.offset + len(selected) < len(rows) else None,
        },
        "crawl": reports,
        "warnings": warnings,
        "scope": (
            "CILRAP public site and FICHL section: bounded crawl, local text matching, "
            "not a complete site index"
        ),
        "evidence": http.evidence,
    }


def fetch(locator: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    parsed = urlparse(locator)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() != "www.cilrap.org":
        raise ValueError("fetch expects an https://www.cilrap.org/ URL")
    max_bytes = args.max_mb * 1024 * 1024
    body, meta = http.get(locator, headers=_headers())
    if len(body) > max_bytes:
        raise RetrievalError(f"Response exceeds --max-mb ({args.max_mb} MiB)")
    if body.startswith(b"%PDF"):
        pages = pdf_pages(body)
        text = "\n\n".join(f"@@PAGE {p['page']}@@\n{p['text']}" for p in pages)
        if args.pdf_out:
            Path(args.pdf_out).write_bytes(body)
        if args.text_out:
            Path(args.text_out).write_text(text, encoding="utf-8")
        return {
            "status": "ok",
            "url": meta["source_url"],
            "pages": len(pages),
            "needs_ocr": not any(p["text"].strip() for p in pages),
            "page_text": pages,
            "pdf_out": str(Path(args.pdf_out).resolve()) if args.pdf_out else None,
            "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
            "sha256": meta["sha256"],
            "retrieved_at": meta["retrieved_at"],
        }
    soup = BeautifulSoup(body, "html.parser")
    container = soup.select_one("main") or soup.select_one("article") or soup.body or soup
    for node in container.select("script, style, nav, header, footer, input, select, button, textarea, noscript"):
        node.decompose()
    text = container.get_text("\n", strip=True)
    if len(text) < 100:
        raise RetrievalError("Insufficient CILRAP page text")
    links = []
    seen = set()
    for anchor in container.select("a[href]"):
        href = urljoin(meta["source_url"], anchor["href"])
        if href in seen:
            continue
        seen.add(href)
        links.append({"text": clean(anchor.get_text(" ", strip=True)), "url": href})
    if args.text_out:
        Path(args.text_out).write_text(text, encoding="utf-8")
    return {
        "status": "ok",
        "url": meta["source_url"],
        "title": clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
        "text": text,
        "text_characters": len(text),
        "document_links": links,
        "content_scope": "CILRAP HTML page text; linked PDFs must be fetched separately",
        "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
        "sha256": meta["sha256"],
        "retrieved_at": meta["retrieved_at"],
    }


def doctor(args: argparse.Namespace) -> dict[str, Any]:
    checks = [
        {"check": "python", "ok": True, "detail": "Python runtime available"},
        {"check": "requests", "ok": True, "detail": "requests importable"},
        {"check": "beautifulsoup4", "ok": True, "detail": "bs4 importable"},
    ]
    if args.no_probe:
        return {"ok": True, "status": "ok (probes skipped)", "checks": checks}
    http = make_http(args)
    probes = []
    for scope, url in (("cilrap", "https://www.cilrap.org/"), ("fichl", "https://www.cilrap.org/fichl")):
        try:
            soup, meta = http.soup(url, headers=_headers())
            probes.append(
                {
                    "check": scope,
                    "ok": bool(soup.title),
                    "http_status": meta["http_status"],
                    "bytes": meta["bytes"],
                }
            )
        except Exception as exc:
            probes.append({"check": scope, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
    checks.extend(probes)
    ok = any(item.get("ok") for item in probes)
    return {"ok": ok, "status": "ok" if ok else "error", "checks": checks, "catalog": {"seeds": SEEDS}}
