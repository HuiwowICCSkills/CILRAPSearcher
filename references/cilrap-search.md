# CILRAP/FICHL 实测记录（2026-11-09）

## 站点

- CILRAP 种子：`/purpose`、`/thematic-libraries`、`/events`、`/news`
- FICHL 种子：`https://www.cilrap.org/fichl`
- 实测 `/fichl` 返回 200、27,714 字节，标题 `Forum for International Criminal and Humanitarian Law`
- `fichl.org` 独立域名当前 SSL 连接失败；规范入口是 `cilrap.org/fichl`

## 检索

`transitional justice --scope fichl --max-pages 5 --limit 3` → `status=partial`、`total=2`，`crawl[0].exhaustive=false`。

## 解析

- 只允许 `www.cilrap.org`；CILRAP scope 路径 `/`，FICHL scope 路径 `/fichl`
- 页面文本和 PDF 页文本均参与本地匹配
- 链接标题命中标为 `http-catalogue-link`，目标页未必读取

## 边界

- 没有稳定公开全文检索 API；`wp-json/wp/v2/search` 实测 404
- `max-pages` 和 `depth` 只控制爬取预算，不改变覆盖不完整的事实
