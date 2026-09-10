# Exile UI Act Tracker 中文翻译提示词

你正在翻译 Exile UI 的 Act Tracker 攻略步骤。输入是 JSONL，每行一个独立对象。

只允许修改以下字段：

- `translation`：填写目标语言译文。
- `status`：确定无误填 `translated`；术语、缩写或语义不确定填 `needs-review`。
- 可选 `note`：简短说明疑点。

必须遵守：

1. 翻译 `masked_source` 的整句含义，按自然中文重排语序，不做逐词替换。
2. 每一个 `__XUI_TOKEN_###__` 必须原样保留且只出现一次；可以移动其位置。
3. `glossary` 中出现的实体采用 `name_zh` 对应的简体中文术语。
4. 文字要短、明确，适合游戏覆盖层。保留数值、方向和先后关系。
5. 不添加原文没有的路线判断，不删除“可选/开荒/小号”等条件。
6. 不确定的缩写（例如 `qs`、`ms`、布局提示）不要擅自扩写；标记 `needs-review`。
7. 不修改 `id`、`file`、`path`、`source`、`source_hash`、`masked_source`、`tokens`、`glossary`。
8. 输出仍为 JSONL；不要加 Markdown 代码围栏或说明文字。
9. 渲染器以 ASCII 空格结束 `(color:...)`、`arena:` 和 `(quest:...)` 的颜色作用域。彩色名词后的“与、位于、取得、通往”等后续叙述必须与该名词留出空格，不能粘成同一个分词。

中文风格：使用“进入、击杀、传送、回城、领取、购买”等简短动词开头；区域、NPC、
Boss、任务物品、技能石名称优先保证与游戏客户端一致，其次才考虑字面通顺。

\n