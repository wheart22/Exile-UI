# 故障排查

## 语言下拉框中没有 `zh-CN`

请确认已将压缩包内的 `data\zh-CN` 合并到 Exile UI 根目录的 `data` 文件夹，并完全
退出后重新启动 Exile UI。语言包不修改上游 AHK 源码，也不包含 `client.txt`。

## PoB 导入后宝石仍显示英文

请确认使用的是本分支构建的 `data\zh-CN\[leveltracker] gems.json`，并且没有被旧语言包
覆盖。该文件保留英文内部键，只在条目中加入“简体中文名（English name）”；PoB 导入和
英文搜索逻辑不需要修改。

## 指南中的区域名仍显示英文

区域名称来自 `data\zh-CN\[leveltracker] areas.json`。重新生成语言包后再安装，或删除
旧的 `data\zh-CN` 后重新解压。若问题仍存在，请记录 Exile UI 上游提交号和当前语言包
版本。

## 没有 PoE1 时如何查看界面

完整覆盖层需要游戏窗口；没有客户端时请双击根目录的 `Exile UI - Offline Preview.ahk`。
该模式会读取当前 `zh-CN` 的界面、剧情和宝石数据，供本地检查翻译，不会启动游戏联动功能。
