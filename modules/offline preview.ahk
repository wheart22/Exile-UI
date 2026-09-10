OfflinePreview_Start()
{
	local
	global vars, Json

	vars.lang := Lang_Load("zh-CN/UI.txt")
	vars.lang2 := Lang_Load("english/UI.txt")
	vars.offline_gems := Json.Load(LLK_FileRead("data\zh-CN\[leveltracker] gems.json", 1, "65001"))
	vars.offline_labels := Json.Load(LLK_FileRead("data\zh-CN\[leveltracker] guide labels.json", 1, "65001"))
	vars.offline_guide := Json.Load(LLK_FileRead("data\zh-CN\[leveltracker] default guide.json", 1, "65001"))

	If !IsObject(vars.offline_gems) || !IsObject(vars.offline_labels) || !IsObject(vars.offline_guide)
	{
		MsgBox,, Exile UI, Offline preview data is missing. Please run this file from the complete Exile UI folder.
		ExitApp
	}

	Gui, offline_preview: New, +Resize +MinSize900x600 +OwnDialogs +LabelOfflinePreview
	Gui, offline_preview: Color, 171717
	Gui, offline_preview: Font, s10 cFFFFFF, Microsoft YaHei
	Gui, offline_preview: Add, Text, x24 y18 cFFFFFF, % "Exile UI - PoE1 " OfflinePreview_T("global_preview")
	Gui, offline_preview: Add, Text, x24 y48 cAAAAAA, % OfflinePreview_T("m_general_language") " zh-CN | " OfflinePreview_T("m_general_display") " 1280x720"
	Gui, offline_preview: Add, Text, x24 y70 cFFCC66, % OfflinePreview_T("global_troubleshoot") ": offline preview"
	Gui, offline_preview: Add, Tab2, x20 y98 w960 h470 vOfflinePreviewTab, % OfflinePreview_T("ms_general") "|" OfflinePreview_T("ms_leveling tracker") "|PoB " OfflinePreview_T("global_gem")

	Gui, offline_preview: Tab, 1
	Gui, offline_preview: Add, GroupBox, x44 y132 w420 h350, % OfflinePreview_T("global_ui")
	Gui, offline_preview: Add, Text, x70 y168 w370, % OfflinePreview_T("m_general_language")
	Gui, offline_preview: Add, Text, x250 y168 c66FF99, zh-CN - Simplified Chinese
	Gui, offline_preview: Add, Text, x70 y204 w370, % OfflinePreview_T("m_general_display")
	Gui, offline_preview: Add, Text, x250 y204 c66FF99, % OfflinePreview_T("m_general_display", 3)
	Gui, offline_preview: Add, Text, x70 y240 w370, % OfflinePreview_T("global_enable")
	Gui, offline_preview: Add, Text, x250 y240 c66FF99, % OfflinePreview_T("global_positive")
	Gui, offline_preview: Add, Text, x70 y276 w370, % OfflinePreview_T("global_hotkey")
	Gui, offline_preview: Add, Text, x250 y276 c66FF99, Ctrl + Space
	Gui, offline_preview: Add, Text, x70 y312 w370, % OfflinePreview_T("m_general_resolution", 2)
	Gui, offline_preview: Add, Text, x250 y312 c66FF99, 1280 x 720
	Gui, offline_preview: Add, Text, x70 y348 w370, % OfflinePreview_T("global_font")
	Gui, offline_preview: Add, Text, x250 y348 c66FF99, Microsoft YaHei

	Gui, offline_preview: Add, GroupBox, x500 y132 w440 h350, % OfflinePreview_T("global_info")
	Gui, offline_preview: Add, Text, x526 y168 w390, % "Exile UI: " OfflinePreview_T("global_window")
	Gui, offline_preview: Add, Text, x526 y204 w390, % OfflinePreview_T("ms_actdecoder")
	Gui, offline_preview: Add, Text, x526 y240 w390, % OfflinePreview_T("ms_leveling tracker")
	Gui, offline_preview: Add, Text, x526 y276 w390, % OfflinePreview_T("ms_screen-checks")
	Gui, offline_preview: Add, Text, x526 y312 w390, % OfflinePreview_T("ms_search-strings")
	Gui, offline_preview: Add, Text, x526 y348 w390, % OfflinePreview_T("ms_stash-ninja")
	Gui, offline_preview: Add, Text, x526 y396 w390 cAAAAAA, % "PoE1 zh-CN | upstream-compatible data keys"

	Gui, offline_preview: Tab, 2
	Gui, offline_preview: Add, Text, x44 y132 cFFFFFF, % OfflinePreview_T("ms_leveling tracker")
	Gui, offline_preview: Add, Text, x44 y160 w890 cAAAAAA, % OfflinePreview_T("lvltracker_gempickups") " / " OfflinePreview_T("lvltracker_editor")
	Gui, offline_preview: Add, ListView, x44 y194 w896 h280 Grid vOfflinePreviewGuideList, % OfflinePreview_T("lvltracker_editor_acts") "|" OfflinePreview_T("global_preview")

	Gui, offline_preview: Tab, 3
	Gui, offline_preview: Add, Text, x44 y132 w890, % OfflinePreview_T("lvltracker_gemnotes")
	Gui, offline_preview: Add, Edit, x44 y164 w700 h28 vOfflinePreviewGemSearch
	Gui, offline_preview: Add, Button, x756 y164 w84 h28 gOfflinePreview_Search, % OfflinePreview_T("global_search")
	Gui, offline_preview: Add, Button, x850 y164 w90 h28 gOfflinePreview_Clear, % OfflinePreview_T("global_clear")
	Gui, offline_preview: Add, Text, x44 y200 w896 cAAAAAA vOfflinePreviewGemCount
	Gui, offline_preview: Add, ListView, x44 y226 w896 h248 Grid vOfflinePreviewGemList, % OfflinePreview_T("global_name") " (key)" "|" OfflinePreview_T("global_name") "|" OfflinePreview_T("global_type") "|" OfflinePreview_T("m_general_level")

	Gui, offline_preview: Tab
	Gui, offline_preview: Add, Text, x24 y586 w930 cAAAAAA, % "Offline preview only: game window, client log, OCR, screen checks and in-game overlays require Path of Exile."
	Gui, offline_preview: Show, w1000 h630, Exile UI - Offline Preview

	OfflinePreview_FillGuide()
	OfflinePreview_FillGems()
}

OfflinePreview_T(key, index := 1)
{
	local
	global vars

	value := vars.lang[key][index]
	If (value = "")
		value := vars.lang2[key][index]
	Return value = "" ? key : value
}

OfflinePreview_CleanGuide(text)
{
	global vars

	Loop
	{
		If !RegExMatch(text, "<([^>]*)>", match)
			Break
		label := match1, display := IsObject(vars.offline_labels) && vars.offline_labels.HasKey(label) ? vars.offline_labels[label] : label
		text := StrReplace(text, "<" label ">", display,, 1)
	}
	text := RegExReplace(text, "\((?:img|color|hint):[^)]*\)", "")
	text := RegExReplace(text, "<([^>]*)>", "$1")
	text := StrReplace(text, ";;", " -> ")
	text := StrReplace(text, "`n", " ")
	Return Trim(text, " `t")
}

OfflinePreview_FillGuide()
{
	local
	global vars

	Gui, offline_preview: ListView, OfflinePreviewGuideList
	LV_Delete()
	For act, step in vars.offline_guide
	{
		text := IsObject(step[1]) ? step[1][1] : step[1]
		LV_Add("", OfflinePreview_T("lvltracker_format_act") act, OfflinePreview_CleanGuide(text))
	}
	LV_ModifyCol(1, 100)
	LV_ModifyCol(2, "AutoHdr")
}

OfflinePreview_GemAttribute(attribute)
{
	If (attribute = 1)
		Return "Strength"
	If (attribute = 2)
		Return "Dexterity"
	If (attribute = 3)
		Return "Intelligence"
	Return "-"
}

OfflinePreview_FillGems(filter := "")
{
	local
	global vars
	count := 0

	Gui, offline_preview: ListView, OfflinePreviewGemList
	LV_Delete()
	For key, gem in vars.offline_gems
	{
		If (SubStr(key, 1, 1) = "_")
			Continue
		name := gem.name ? gem.name : key
		If filter && !InStr(key, filter) && !InStr(name, filter)
			Continue
		attribute := OfflinePreview_GemAttribute(gem.attribute)
		LV_Add("", key, name, attribute, gem.level ? gem.level : "-")
		count += 1
	}
	LV_ModifyCol(1, 220)
	LV_ModifyCol(2, 390)
	LV_ModifyCol(3, 100)
	LV_ModifyCol(4, 60)
	GuiControl, offline_preview:, OfflinePreviewGemCount, % count " / PoE1 gem entries"
}

OfflinePreview_Search()
{
	global OfflinePreviewGemSearch

	Gui, offline_preview: Submit, NoHide
	OfflinePreview_FillGems(OfflinePreviewGemSearch)
}

OfflinePreview_Clear()
{
	global OfflinePreviewGemSearch

	GuiControl, offline_preview:, OfflinePreviewGemSearch
	OfflinePreviewGemSearch := ""
	OfflinePreview_FillGems()
}

OfflinePreviewClose()
{
	ExitApp
}

OfflinePreviewEscape()
{
	ExitApp
}
