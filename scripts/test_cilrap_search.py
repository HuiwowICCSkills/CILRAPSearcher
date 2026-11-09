"""Offline tests for CILRAPSearcher."""
from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import cilrap_adapter as adapter  # noqa: E402


def meta(url):
    return {"source_url": url, "http_status": 200, "content_type": "text/html",
            "bytes": 100, "retrieved_at": "2026-11-09T00:00:00Z", "sha256": "0" * 64}


class FakeHttp:
    def __init__(self):
        self.evidence = []

    def get(self, url, params=None, headers=None):
        html = "<html><head><title>FICHL</title></head><body>Transitional justice and publication series.</body></html>"
        return html.encode("utf-8"), meta(url)


def args(**kwargs):
    base = dict(scope="fichl", limit=2, offset=0, max_pages=2, depth=1,
                cache=".cache", offline=False, cache_ttl=0, timeout=30)
    base.update(kwargs)
    return argparse.Namespace(**base)


class CilrapTests(unittest.TestCase):
    def test_bounded_search_returns_partial(self):
        out = adapter.search("transitional justice", args(), FakeHttp())
        self.assertEqual(out["status"], "partial")
        self.assertGreaterEqual(out["total"], 1)
        self.assertFalse(out["crawl"][0]["exhaustive"])


if __name__ == "__main__":
    unittest.main()
