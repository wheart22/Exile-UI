# PoE1 简体中文本地化规则

## 范围

- `zh-CN` 是唯一发布语言；
- 上游 PoE1/PoE2 程序和英文数据保持不变；
- 只构建 PoE1 UI、主线指南、区域表、帮助文本和 PoB 宝石名称；
- PoE2 指南、PoE2 宝石数据库、中文客户端日志/OCR 和物品文本不在本分支承诺范围内。

## 术语和宝石

游戏专有名词使用中文客户端或 PoEDB 的简体中文术语。PoB 导入得到的宝石仍以英文内部键
匹配；`data/zh-CN/[leveltracker] gems.json` 只在对应条目上增加：

```json
"name": "赦罪（Absolution）"
```

`localization/glossary/gems-zh-CN.json` 必须覆盖上游 `[leveltracker] gems.json` 的每一个非元数据
条目。名称缺失、增加未知键、双语格式不正确，都会使构建失败。除 `name` 外，宝石等级、属性、
任务和商店数据必须逐项保持上游内容。

## 指南标记

翻译时必须保留下列标记的数量和拼写，但可以调整整句中文语序：

- `areaid...`；
- `(img:...)`、`(color:...)`、`(lvl:...)`；
- `(quest:...)`，包括嵌套 `(quest:(...))`；
- `(hint)_...`、`<...>`、`;;`、`||`、`arena:`；
- `leaguestart:`、`twinkrun:`、`optional:`、`kill`。

构建器会把这些标记暂时替换为占位符，并检查它们是否完整恢复。尖括号中的任务或奖励名
会显示给玩家，已知标签应使用 `ANGLE_TOKEN_TRANSLATIONS` 中的简中术语。

## 文件策略

- `UI.txt`：完整翻译发布；
- `[leveltracker] default guide.json`：PoE1 主线指南，必须完整；
- `[leveltracker] areas.json`：由术语库生成的运行时区域名，必须完整；
- `help tooltips.json`：已审校部分使用中文，其余保留英文回退；
- `[leveltracker] gems.json`：完整双语名称，禁止英文回退；
- `client.txt`、`[leveltracker] default guide 2.json` 和 `[leveltracker] gems 2.json`：不发布。

## 审校

每次上游同步后，审阅 `reports/sync.json` 的新增、修改和删除项；重新检查 PoE1 术语、区域
标记、图标动作和颜色边界。完成后执行单元测试、构建、`validate` 和发布包检查。

\n