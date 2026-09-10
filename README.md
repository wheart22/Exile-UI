## Exile UI PoE1 简体中文分支

本分支 `poe1-zh-CN` 基于 [Lailloken/Exile-UI](https://github.com/Lailloken/Exile-UI) 的最新 `main`，保留上游 PoE1/PoE2 程序与英文数据。
中文资源已经合并进完整运行目录，Release 提供解压即用的整合压缩包；PoE2 指南和 PoE2 宝石数据保持英文。

主要包含：

- PoE1 界面、剧情追踪器、主线指南、区域名称和帮助文本；
- PoB 导入后的宝石显示为“简体中文名（English name）”；
- 宝石数据库保留英文内部键，因此英文游戏客户端搜索逻辑不变；
- 不修改上游 AHK 程序，也不添加定时 GitHub Actions。

### 下载与安装整合版

从 [Releases](https://github.com/wheart22/Exile-UI/releases) 下载最新的
`Exile-UI-zh-CN-*.zip`，完整解压到任意目录。压缩包已经包含 Exile UI 程序、全部运行数据和
简体中文 PoE1 资源，不需要再与原版目录合并。

1. 如果没有 AutoHotkey v1.1，请先从 [AutoHotkey](https://www.autohotkey.com/) 安装。
2. 双击解压目录中的 `Exile UI.ahk` 启动程序。
3. PoE1 首次启动默认使用 `zh-CN`；如需切换语言，可在设置的“常规/UI”区域修改。

没有安装 PoE1 时，可双击 `Exile UI - Offline Preview.ahk` 打开离线预览，查看简中界面文案、剧情步骤和
PoB 宝石中英文名称。离线预览不模拟游戏窗口、客户端日志、OCR、画面检测和游戏内覆盖层。

PoB 导入后的主动宝石、辅助宝石和宝石链接会显示为“简体中文名（English name）”；英文游戏客户端
搜索逻辑保持不变。当前版本不包含中文 `client.txt`、物品文本和 OCR 适配。

### 手动同步上游

同步前请确认工作区没有未提交修改：

```powershell
git fetch upstream main
git checkout poe1-zh-CN
git merge upstream/main
python localization/tools/localize.py sync
python localization/tools/localize.py build --locale zh-CN --allow-partial
python localization/tools/localize.py validate
python -m unittest discover -s localization/tests -p "test_*.py"
python localization/tools/package_release.py
```

同步后必须审阅 `localization/reports/sync.json` 中的新增、修改和删除文案；如果上游新增或修改
PoE1 宝石，先更新 `localization/glossary/gems-zh-CN.json`，再重新构建。缺少宝石翻译会阻止正式
发布。完整规则见 [`localization/docs/RELEASE-PROCESS.md`](localization/docs/RELEASE-PROCESS.md)。

## About:
A light-weight AHK overlay with UI and QoL features for Path of Exile 1 and 2, emphasizing ease-of-use, minimalist design, low hotkey requirements, and seamless integration into the game-client. Formerly Lailloken UI.  
**`This project is not affiliated with or endorsed by Grinding Gear Games (GGG) in any way`**.
<br>

## Download & Setup
| [![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_autohotkey.png)](https://www.autohotkey.com/) | [![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_guide.png)](https://github.com/Lailloken/Exile-UI/wiki) | [![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_download.png)](https://github.com/wheart22/Exile-UI/releases) | [![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_releases.png)](https://github.com/wheart22/Exile-UI/releases) |
|---|---|---|---|

## Contributions
| [![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_issues.png)](https://github.com/Lailloken/Exile-UI/issues/new) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_code.png) | [![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/_translations.png)](https://github.com/Lailloken/Exile-UI/issues/326) |
|---|---|---|
<br>

### Context: What is this project?
<details><summary>show</summary>

- this is a fun-project by a self-taught hobby-coder that contains various UI/QoL features

  - I implement ideas that I think are fun/interesting to work on and figure out (even if they're not necessarily useful to everyone, or even myself)

  - since some features are user-requested and I don't use every single one myself, some aspects are heavily reliant on user-feedback (use the banners above to contribute)
 
  - my own ideas are always centered around SSF, but I'm open to trade-league-related ideas (if they're interesting enough and not too complex)
 
  - I generally avoid features that are "OP" or abusable because I don't think they're good for the game, regardless of how much QoL they would provide

- I view this as a personal toolkit rather than a product, so certain aspects may seem rough around the edges (or simply unconventional) when compared to other PoE-related projects
</details>

### Transparency Notice / Things you should know
<details><summary>show</summary>

- **things this tool does**

  - reads the game's client.txt log-file for certain statistics/events: current character level, area & transitions, NPC dialogues, etc.
 
  - sends key-presses to copy item-info, or activate chat-commands and in-game searches
 
  - checks screen-content for context-sensitivity to adapt the tool's behavior: it searches for open UIs (e.g. inventory, stash), `but it never reads/checks game-related values or bars`
 
  - reads on-screen text `on key-press` to summarize the information and display it in customizable tooltips
 
- **FAQ: has GGG approved this / can I be banned?**

  - to my knowledge, GGG has never approved any (local) 3rd-party tool
 
  - I can't make any claims about whether you'll get banned or not. All I can say is that I strictly follow [GGG's guidelines](https://www.pathofexile.com/developer/docs/index#policy): creators can be banned for distributing tools that violate the ToS, so it's in my best interest to follow them
 
  - (weak) anecdotal evidence: I have not been banned, nor have I heard of anyone else being banned
</details>
<br>

## Main Features
**`click the links to open the feature's wiki-page`**
<br>

### [Clone-frames](https://github.com/Lailloken/Exile-UI/wiki/Clone-frames): "interface-customization" by cloning & projecting screen areas  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| examples:<br>rage meter,<br>cooldowns,<br>charges | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/cloneframes_001.jpg) | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/cloneframes_101.jpg) |
<br>

### [Item-info](https://github.com/Lailloken/Exile-UI/wiki/Item-info): compact & customizable tooltip to determine loot quality at a glance  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| example:<br>rare | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/iteminfo_001.png) | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/iteminfo_101.png) |
| example:<br>unique | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/iteminfo_002.png) | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/iteminfo_102.png) |
<br>

### [Act-Tracker](https://github.com/Lailloken/Exile-UI/wiki/Act%E2%80%90Tracker): campaign-related QoL features  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| automated<br>guide | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_001.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_101.png) |
| PoB tree<br>overlays | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_102.jpg) |
| gem-setup<br>overlays | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_003.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_103.jpg) |
| gemcutting<br>overlay | | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/leveltracker_104.jpg) |
<br>

### [Act-Decoder](https://github.com/Lailloken/Exile-UI/wiki/Act%E2%80%90Decoder): campaign layout overlay  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| layout<br>indicators | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/actdecoder_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/actdecoder_101.jpg) |
| full<br>layouts | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/actdecoder_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/actdecoder_102.jpg) |
<br>

### [Stash-Ninja](https://github.com/Lailloken/Exile-UI/wiki/Stash%E2%80%90Ninja): poe.ninja price-overlay for fixed stash tabs
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| customizable<br>price-tags<br>& profiles | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/stashninja_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/stashninja_101.jpg) |
| conversions<br>& price history | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/stashninja_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/stashninja_102.jpg) |
<br>

### [Rune-Ninja](https://github.com/Lailloken/Exile-UI/wiki/Rune%E2%80%90Ninja): poe.ninja price-overlay for runic remnants
**`Path of Exile 2 ONLY`**
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/runeninja_101.jpg) |
|---|
<br>

### [Chat Macros](https://github.com/Lailloken/Exile-UI/wiki/Chat-Macros): quick-access macros and "chat wheels"
| configuration | "chat wheels" |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/chatmacros_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/chatmacros_002.jpg) |
<br>

### [Map-Tracker](https://github.com/Lailloken/Exile-UI/wiki/Map%E2%80%90Tracker): collect, save, view, and export mapping-related data for statistical analysis
| | in-game log viewer |
|---|---|
| PoE | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/maptracker_001.png) |
| PoE2 | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/maptracker_101.png) |
<br>

### Overhauled [map-info panel](https://github.com/Lailloken/Exile-UI/wiki/Map-info-panel): streamlined & customizable map-mod tooltip and panel
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| tooltip | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/mapinfo_001.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/mapinfo_101.png) |
| panel | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/mapinfo_002.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/mapinfo_102.png) |
<br>

### [Sanctum/Sekhema Planner](https://github.com/Lailloken/Exile-UI/wiki/Sanctum-and-Sekhema-Planner): floor scanner, interactive planner, relic manager
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| potential<br>reach,<br>available<br>pathing | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_102.jpg) |
| how to<br>avoid&nbsp;bad<br>rooms | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_003.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_103.jpg) |
| relic<br>manager | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_004.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/sanctum_104.jpg) |
<br>

### [Enchant Finder](https://github.com/Lailloken/Exile-UI/wiki/Enchant-Finder): quick-access enchant calculator for blight oils and distilled emotions
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| easy import<br>of materials | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/anoints_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/anoints_101.jpg) |
| flexible filter:<br>regex/keywords | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/anoints_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/anoints_102.jpg) |
<br>

### [FilterSpoon](https://github.com/Lailloken/Exile-UI/wiki/FilterSpoon): quick-access "in-client" lootfilter editor
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| rule-matching on hover | ![img](https://github.com/user-attachments/assets/cf335e64-1f92-4489-803c-0238110bc963) | ![img](https://github.com/user-attachments/assets/71e19b15-485e-4b51-b3fe-9b80d6eaffc6) |
| manual searching/browsing | ![img](https://github.com/user-attachments/assets/283eabd6-13b1-48e3-9f1f-c7fc1e72cd18) | ![img](https://github.com/user-attachments/assets/2871c7d2-0e8a-4ecc-af36-6848900c1ad9) |
<br>

### [Recombination Simulator](https://github.com/Lailloken/Exile-UI/wiki/Recombination-Simulator): in-game overlay that simulates outcomes in a few clicks
| example 1: single mod transfer | example 2: runic + zeffre + archmage's wand |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/recombination_001.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/recombination_002.png)
<br>

### [Context-menu](https://github.com/Lailloken/Exile-UI/wiki/Minor-Features) for items: single-hotkey access to features and popular 3rd-party websites  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| example:<br>gear | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/contextmenu_001.jpg) | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/contextmenu_101.jpg) |
| examples:<br>cluster jewel,<br>fragments | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/contextmenu_002.jpg) | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/contextmenu_102.jpg) |
| example:<br>timeless jewel | ![img](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/contextmenu_003.jpg) | |
<br>

### [Statlas](https://github.com/Lailloken/Exile-UI/wiki/Statlas): quick-access atlas overlay for map layouts, bosses, and statistics
**`Path of Exile 2 ONLY`**
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/statlas_001.png) |
|---|
<br>

### [Search-strings](https://github.com/Lailloken/Exile-UI/wiki/Search-strings): customizable, single-hotkey menu for every individual in-game search  
| | Path of Exile | Path of Exile 2 |
|---|---|---|
| built-in:<br>beast-crafting | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/searchstrings_001.jpg) | |
| example:<br>Gwennen | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/searchstrings_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/searchstrings_102.jpg) |
| example:<br>vendors | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/searchstrings_003.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/searchstrings_103.jpg) |
<br>

### [Vaal Street](https://github.com/Lailloken/Exile-UI/wiki/Vaal-Street): QoL, tracking, and logging features for the exchange and async trading

**currency exchange:**
| | PoE1 | PoE2 |
|---|---|---|
| optional trade logging | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_001.jpg) | <p align="center">✔️</p> |
| ratio-calculator | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_102.jpg) |
| optional balance tracking | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_003.jpg) | <p align="center">✔️</p> |

**async trade:**
| | PoE1 | PoE2 |
|---|---|---|
| quick repricing | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_010.jpg) | <p align="center">✔️</p> |
| optional sales tracking/logging | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_011.jpg) | <p align="center">✔️</p> |
| optional purchase logging | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_012.jpg) | <p align="center">✔️</p> |
| log-viewer | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/vaalstreet_013.jpg) | <p align="center">✔️</p> |
<br>

### Several minor [QoL features](https://github.com/Lailloken/Exile-UI/wiki/Minor-Features):  
| quick-access overlay and tracker for casual lab-runs | countdown & stopwatch |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/qol_005.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/qol_003.png) |
|| <p align="center">**Path of Exile 2 compatible**</p> |

| in-client notepad & sticky-notes | essence tooltip to check the next tier's stats | map-event notifications |
|---|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/qol_004.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/qol_001.png) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/qol_006.png) |
| <p align="center">**Path of Exile 2 compatible**</p> |||
<br>

### [Cheat-sheet Overlay Toolkit](https://github.com/Lailloken/Exile-UI/wiki/Cheat-sheet-Overlay-Toolkit): create customizable, context-sensitive overlays
**`Path of Exile 2 compatible`**  
| image overlay | app "overlay" | custom/advanced overlay |
|---|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/cheatsheets_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/cheatsheets_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/cheatsheets_003.jpg) |
<br>

### [TLDR-Tooltips](https://github.com/Lailloken/Exile-UI/wiki/TLDR%E2%80%90Tooltips): customizable tooltips that summarize & highlight on-screen information
| eldritch altars | vaal side areas |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/tldr_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/tldr_002.jpg) |
<br>

### [Betrayal-info](https://github.com/Lailloken/Exile-UI/wiki/Betrayal-Info): streamlined & customizable info-sheet (with optional image recognition)  
| simple mode: member-list & custom highlighting | img-recognition: on-hover reward list + board tracking |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/betrayal_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/betrayal_002.jpg) |
<br>

### Support for [community translations](https://github.com/Lailloken/Exile-UI/discussions/categories/translations-localization):
| item-info tooltip in German | item-info tooltip in Japanese | map-info panel in German |
|---|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/translations_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/translations_002.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/translations_003.jpg) |
<br>
<br>

### Acknowledgements
- various features use data derived from [Path of Building](https://github.com/PathOfBuildingCommunity/PathOfBuilding), [poe ladder](https://poeladder.com/), and [poedb](https://poedb.tw/us/)

- `act-tracker` has a default guide and PoB-import features that were originally derived from [exile-leveling](https://github.com/HeartofPhos/exile-leveling)

- `stash-ninja` and `rune-ninja` use price data provided by [poe.ninja](https://poe.ninja/)

- [GDI+ Library for AutoHotkey](https://github.com/marius-sucan/AHK-GDIp-Library-Compilation), [GDI+ ImageSearch](https://github.com/MasterFocus/AutoHotkey/blob/master/Functions/Gdip_ImageSearch/Gdip_ImageSearch.ahk), [OCR with UWP API](https://www.autohotkey.com/boards/viewtopic.php?t=72674) enable advanced screen/image-related features

- [AutoHotkey-JSON](https://github.com/cocobelgica/AutoHotkey-JSON) enables processing JSON databases

- [base64 decode for AutoHotkey](https://github.com/jNizM/AHK_Scripts/blob/master/src/encoding_decoding/base64.ahk) enables decoding PoB-exports

- [zlib wrapper for AutoHotkey](https://www.autohotkey.com/board/topic/63343-zlib/) enables decompressing and processing PoB-exports
<br>

### (Temporarily-)retired / Legacy Features:
| [Archnemesis Recipe Helper/Scanner](https://github.com/Lailloken/Exile-UI/wiki/%5BArchive%5D-Retired-Features#archnemesis-recipe-scanner) | [Delve-helper](https://github.com/Lailloken/Exile-UI/wiki/%5BArchive%5D-Retired-Features#delve-helper): in-game UI to help you find secret passages |
|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/legacy_001.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/legacy_002.jpg) |

| [Necropolis Lantern Highlighting](https://github.com/Lailloken/Exile-UI/wiki/%5BArchive%5D-Retired-Features#necropolis-lantern-highlighting) | [Overlayke: Kalandra Planner/Preview Overlay](https://github.com/Lailloken/Exile-UI/wiki/%5BArchive%5D-Retired-Features#overlayke-lake-of-kalandra-plannerpreview-overlay) | [Sanctum-room tooltip overlays](https://github.com/Lailloken/Exile-UI/releases/tag/v1.29.4-hotfix2) |
|---|---|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/necropolis_003.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/legacy_004.jpg) | ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/legacy_005.jpg) |

| [Seed-explorer](https://github.com/Lailloken/Exile-UI/wiki/%5BArchive%5D-Retired-Features#seed-explorer-in-client-ui-for-timeless-jewels): in-client UI to quickly test a legion jewel in every socket |
|---|
| ![image](https://raw.githubusercontent.com/Lailloken/Exile-UI/main/img/readme/seedexplorer_001.jpg) |
