---
name: CILRAPSearcher
description: 独立检索 CILRAP 公共网站及其 FICHL 板块，按关键词做有界 HTML/PDF 爬取和本地文本匹配；明确报告覆盖为 bounded crawl，不是全站全文数据库。
---

# CILRAPSearcher

> **`<skill-dir>`** = 本 SKILL.md 所在目录。核心脚本为 `<skill-dir>/scripts/cilrap_search.py`；Windows 用 `<skill-dir>/run.ps1`，macOS/Linux 用 `<skill-dir>/run.sh`。部署与排错见 [README.md](README.md)。

这个 skill 只做 `www.cilrap.org` 一个站点，包含 CILRAP 主站和 `/fichl` 板块：

- `search --scope cilrap|fichl|all`：从固定种子页面开始有界爬取，匹配页面文本、PDF 页文本和链接标题；
- 返回 `crawl[].pages_attempted`、`queued_unvisited`、`exhaustive:false`，明确不是全站索引；
- `fetch` 读取单个页面或 PDF。

## 命令

```powershell
& '<skill-dir>/run.ps1' search "transitional justice" --scope fichl --max-pages 12 --depth 1 --limit 10 --out './fichl.json'
& '<skill-dir>/run.ps1' search "thematic libraries" --scope cilrap --max-pages 20 --limit 10 --out './cilrap.json'
& '<skill-dir>/run.ps1' fetch 'https://www.cilrap.org/fichl' --out './fichl-page.json' --text-out './fichl-page.txt'
& '<skill-dir>/run.ps1' doctor
```

通用参数：`--out`、`--cache`、`--cache-ttl`、`--offline`、`--timeout`。`search` 另有 `--scope`、`--limit`、`--offset`、`--max-pages`、`--depth`；`fetch` 另有 `--text-out`、`--pdf-out`、`--max-mb`。

## 结果边界

- CILRAP 没有稳定的公开全文检索 API；本 skill 只能做 bounded crawl，不能承诺全站覆盖。
- FICHL 是 CILRAP 的一个板块；`fichl.org` 不再作为独立站点，规范入口是 `www.cilrap.org/fichl`。
- `status=partial` 是正常状态；`crawl[].exhaustive=false` 必须保留。`queued_unvisited` 表示还有未抓取链接。
- 对 CILRAP 的 CLICC/判例记录/要件/准备工作文件等体系化内容，优先使用 `LexsitusSearcher`；FICHL/TOAEP 出版物优先用 `LegalToolsSearcher` 或 `TOAEP` 渠道。

## 参考

- 2026-11-09 实测：CILRAP/FICHL 页面、种子、bounded crawl 与 FICHL 命中：[references/cilrap-search.md](references/cilrap-search.md)
- 部署、环境与排错：[README.md](README.md)
