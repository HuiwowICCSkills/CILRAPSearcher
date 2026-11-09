# CILRAPSearcher 部署指引

独立检索 CILRAP 公共网站及其 FICHL 板块。只访问 `www.cilrap.org`。

仓库：<https://github.com/HuiwowICCSkills/CILRAPSearcher>（公开）。

## 环境

Python 3.10+，依赖 `requests`、`beautifulsoup4`、`pypdf`；无需登录。

## 安装与自检

```powershell
git clone https://github.com/HuiwowICCSkills/CILRAPSearcher.git "$env:USERPROFILE\.codex\skills\CILRAPSearcher"
python -m pip install -r "$env:USERPROFILE\.codex\skills\CILRAPSearcher\requirements.txt"
& "$env:USERPROFILE\.codex\skills\CILRAPSearcher\run.ps1" doctor
```

## 使用

```powershell
$cilrap = "$env:USERPROFILE\.codex\skills\CILRAPSearcher\run.ps1"
& $cilrap search "transitional justice" --scope fichl --max-pages 12 --depth 1 --limit 10 --out './fichl.json'
& $cilrap search "thematic libraries" --scope cilrap --max-pages 20 --limit 10 --out './cilrap.json'
& $cilrap fetch 'https://www.cilrap.org/fichl' --out './page.json' --text-out './page.txt'
```

## 边界

- 本 skill 只能做 bounded crawl；`exhaustive=false` 和 `queued_unvisited` 必须保留。
- FICHL 是 CILRAP 的板块，`fichl.org` 已不是独立可用站点；规范入口为 `www.cilrap.org/fichl`。
- 体系化的 CLICC/判例记录请用 `LexsitusSearcher`；FICHL/TOAEP 出版物请用 `LegalToolsSearcher` 或 `TOAEP` 渠道。

## 实测效果（2026-11-09）

以下命令与结果来自本机 `~/.codex/skills/CILRAPSearcher` 的实网运行；检索日期 2026-11-09（Asia/Shanghai），输出为该次运行实际返回的 JSON 报告。

```powershell
$cilrap = "$env:USERPROFILE\.codex\skills\CILRAPSearcher\run.ps1"
& $cilrap search 'international criminal justice' --scope all --max-pages 12 --depth 1 --limit 5
```

- 状态：`partial`；bounded crawl 未穷尽（`exhaustive=false`），`total = 16` 是本次已访问页面中的匹配数，不是 CILRAP 全站命中数；本次返回 5 条。
- crawl 字段：`scope=cilrap` 时 `pages_attempted=12`、`queued_unvisited=177`、`matched_in_visited_pages=20`、`errors=[]`、`exhaustive=false`；`scope=fichl` 时 `pages_attempted=3`、`queued_unvisited=0`、`matched_in_visited_pages=3`、`exhaustive=false`。
- `scope` 原文：`CILRAP public site and FICHL section: bounded crawl, local text matching, not a complete site index`。
- 代表性结果：

| 题名 | 类型 / 日期 | 链接 |
| --- | --- | --- |
| Home | retrieved_metadata；— | https://www.cilrap.org/purpose |
| Online thematic libraries | retrieved_metadata；— | https://www.cilrap.org/thematic-libraries |
| Events | retrieved_metadata；— | https://www.cilrap.org/events |
| The Frontiers of International Criminal Law and Justice | retrieved_metadata；— | https://www.cilrap.org/251201/ |
| Power in International Criminal Justice: Towards a Sociology of International Justice | retrieved_metadata；— | https://www.cilrap.org/events/171028-29-florence/ |

> 说明：前三条 `via=http-local-text`、`access=page text; bounded crawl`，命中的是已抓取页面正文里的本地文本匹配，且多为导航/栏目页，不是文献条目；后两条 `via=http-catalogue-link`、`access=link-label-only; target not fetched`，只有链接文字，目标页未抓取。JSON 中没有 `date`、`author` 字段，日期列留空，不补写。`total=16` 与 `crawl` 里的 `matched_in_visited_pages`（cilrap=20、fichl=3）不是同一计数口径；未访问的 `queued_unvisited=177` 个页面不在本次结果范围内，因此不能把 `partial` 读成"站内只有 16 条相关材料"，也不能读成全部已检完。
