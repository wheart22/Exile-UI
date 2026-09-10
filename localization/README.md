# PoE1 简体中文本地化工作区

这里维护 `poe1-zh-CN` 分支的 PoE1 简体中文资源。上游程序和 `data/english` 必须保持原样；
PoE2 的程序、英文数据和英文指南保留在分支中，但不生成 PoE2 中文语言包。

## 文件职责

- `translations/zh-CN.jsonl`：UI、PoE1 主线指南和帮助文本的翻译记忆；
- `glossary/`：PoE1 官方术语和任务标签；
- `glossary/gems-zh-CN.json`：PoB 宝石名称的完整双语映射；
- `tools/localize.py`：同步、构建、校验和安装；
- `tools/package_release.py`：生成只含 `data/zh-CN` PoE1 资源的压缩包。

宝石映射保留英文内部键，只为每个 PoE1 条目加入 `name`，格式为
`简体中文名（English name）`。因此 PoB 导入和英文游戏客户端搜索仍使用原始英文键。

## 常用流程

```powershell
python localization/tools/localize.py sync
python -m unittest discover -s localization/tests -p "test_*.py"
python localization/tools/localize.py build --locale zh-CN --allow-partial
python localization/tools/localize.py validate
python localization/tools/package_release.py
```

构建完成后，使用 `localize.py install --locale zh-CN` 将语言文件安装到 `data/zh-CN`。
`--allow-partial` 只允许帮助文本保留英文回退；PoE1 UI、主线指南、区域表和宝石映射仍必须
通过正式发布校验。

## 上游更新

仓库已配置：

```powershell
git remote add upstream https://github.com/Lailloken/Exile-UI.git
```

上游同步是手动操作，不使用 GitHub Actions：

```powershell
git fetch upstream main
git checkout poe1-zh-CN
git merge upstream/main
python localization/tools/localize.py sync
```

记录 `git log -1 upstream/main` 的提交号，检查 `localization/reports/sync.json` 的新增、修改、
删除项，并审阅所有受影响的 PoE1 文案。若 `[leveltracker] gems.json` 新增或修改条目，必须
先更新 `glossary/gems-zh-CN.json`；映射不完整时 `build` 和正式发布都会失败。

## 范围说明

- 发布：`UI.txt`、PoE1 `[leveltracker] default guide.json`、PoE1 `[leveltracker] areas.json`、
  PoE1 `[leveltracker] gems.json` 和帮助文本；
- 不发布：`client.txt` 的完整中文客户端日志适配、PoE2 指南、PoE2 宝石数据库、繁体中文资源；
- 不修改：PoB XML/`pobb.in` 导入逻辑、英文宝石搜索逻辑和上游 AHK 程序。

\n