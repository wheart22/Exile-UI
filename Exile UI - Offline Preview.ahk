#NoEnv
#SingleInstance Force
#Requires AutoHotkey >=1.1.36 <2 64-bit
SetWorkingDir %A_ScriptDir%
Run, % """" A_AhkPath """ """ A_ScriptDir "\Exile UI.ahk"" --offline", %A_ScriptDir%, UseErrorLevel
If ErrorLevel
	MsgBox,, Exile UI, Could not start the offline preview. Please install AutoHotkey v1.1 64-bit.
ExitApp
