# CILRAPSearcher 部署指引

独立检索 CILRAP 公共网站及其 FICHL 板块。只访问 `www.cilrap.org`。

仓库：<https://github.com/HuiwowICCSkills/CILRAPSearcher>（私有）。

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
