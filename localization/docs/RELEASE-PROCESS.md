# 发布与上游同步流程

## 发布内容

语言包只发布 `zh-CN`，并且只包含 PoE1 资源：

- `UI.txt`；
- `help tooltips.json`；
- `[leveltracker] default guide.json`；
- `[leveltracker] areas.json`；
- `[leveltracker] gems.json`。

不发布 PoE2 指南、PoE2 宝石数据库、繁体中文资源，也不把未完成的 `client.txt` 中文翻译放入
语言包。上游 AHK 源码不被构建或安装流程修改。

## 构建和检查

```powershell
python localization/tools/localize.py sync
python -m unittest discover -s localization/tests -p "test_*.py"
python localization/tools/localize.py build --locale zh-CN --allow-partial
python localization/tools/localize.py validate
python localization/tools/package_release.py
```

正式发布要求 UI、PoE1 主线指南、区域表和宝石数据库全部完整。帮助文本允许未覆盖条目回退
到英文，但必须保留完整 JSON 结构。宝石数据库不允许回退：映射缺少任何上游条目时，构建和
发布校验都会失败。

压缩包位于 `localization/releases/<版本>/`，其内容为：

- `Exile-UI-zh-CN-<版本>.zip`；
- `manifest.json`；
- `SHA256SUMS.txt`。

压缩包内语言文件使用 `data/zh-CN/` 根目录布局，并附带 `安装说明.txt`。

## 手动同步上游

不要添加 GitHub Actions。使用本地 `upstream` remote：

```powershell
git fetch upstream main
git checkout poe1-zh-CN
git merge upstream/main
python localization/tools/localize.py sync
```

同步后记录 `git log -1 --format=%H upstream/main`，审阅 `localization/reports/sync.json` 中的
新增、修改和删除项。修改过的翻译必须重新审校；新出现的 PoE1 宝石要先加入
`localization/glossary/gems-zh-CN.json`，并确认名称采用 `简体中文（English）` 格式。

建议在提交前检查：

```powershell
git diff --stat upstream/main...poe1-zh-CN
git status --short
```

当前分支的 `main` 不参与合并；发布分支只从 `upstream/main` 手动更新。

\n