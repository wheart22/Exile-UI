import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE = Path(__file__).parents[1] / "tools" / "localize.py"
SPEC = importlib.util.spec_from_file_location("exile_localize", MODULE)
localize = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(localize)


class TokenTests(unittest.TestCase):
    def test_txt_value_parser_excludes_quoted_inline_comment(self):
        line = '\tglobal_custom = "custom"\t;## as in "user-defined"'
        match = localize.KEY_VALUE_RE.match(line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), "global_custom")
        self.assertEqual(match.group(2), "custom")

    def test_txt_value_parser_keeps_quotes_inside_value(self):
        line = '\tlog_betrayal = "Guff "Tiny" Grenn:"'
        match = localize.KEY_VALUE_RE.match(line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(2), 'Guff "Tiny" Grenn:')

    def test_tokens_can_be_reordered_and_are_localized(self):
        source = "leaguestart: kill brutus in areaid1_1_7_2 (img:arena) ;; upper prison"
        masked, tokens = localize.mask_tokens(source, "zh-CN")
        placeholders = localize.PLACEHOLDER_RE.findall(masked)
        translated = " ".join(reversed(placeholders)) + " 完成步骤"
        restored = localize.restore_tokens(translated, tokens)
        self.assertIn("开荒:", restored)
        self.assertIn("击杀", restored)
        self.assertIn("areaid1_1_7_2", restored)
        self.assertIn("(img:arena)", restored)
        self.assertIn(";;", restored)

    def test_missing_placeholder_is_rejected(self):
        masked, tokens = localize.mask_tokens("enter areaid1_1_2 (img:waypoint)", "zh-CN")
        with self.assertRaises(ValueError):
            localize.restore_tokens(masked.replace("__XUI_TOKEN_001__", ""), tokens)

    def test_condition_values_are_not_translation_units(self):
        value = {"condition": ["league-start", "yes"], "lines": ["kill boss"]}
        strings = [text for _, text in localize.walk_strings(value)]
        self.assertEqual(strings, ["kill boss"])

    def test_quest_label_keeps_syntax_but_localizes_display(self):
        masked, tokens = localize.mask_tokens("take (quest:golden_hand) and (quest:(book))", "zh-CN")
        restored = localize.restore_tokens(masked, tokens)
        self.assertEqual(restored, "take (quest:黄金之手) and (quest:(技能之书))")

    def test_known_visible_angle_text_and_reward_are_localized(self):
        masked, tokens = localize.mask_tokens(
            '<type_"/passives"_in_chat> then <armor>',
            "zh-CN",
        )
        restored = localize.restore_tokens(masked, tokens)
        self.assertEqual(restored, '<在聊天框中输入_"/passives"> then <护甲>')

    def test_quest_angle_key_is_preserved_for_routing(self):
        masked, tokens = localize.mask_tokens("<enemy_at_the_gate> and <the_siren's_cadence>", "zh-CN")
        self.assertEqual(
            localize.restore_tokens(masked, tokens),
            "<enemy_at_the_gate> and <the_siren's_cadence>",
        )

    def test_quest_angle_key_has_a_chinese_display_label(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / localize.GUIDE_LABELS_NAME
            done, total = localize.build_guide_labels("zh-CN", destination)
            labels = localize.read_json(destination)
        self.assertEqual((done, total), (len(localize.ANGLE_TOKEN_TRANSLATIONS["zh-CN"]),) * 2)
        self.assertEqual(labels["enemy at the gate"], "大门口的敌人")
        self.assertEqual(labels["the siren's cadence"], "海妖之歌")

    def test_unknown_visible_angle_text_is_preserved(self):
        masked, tokens = localize.mask_tokens("<future_upstream_label>", "zh-CN")
        self.assertEqual(localize.restore_tokens(masked, tokens), "<future_upstream_label>")

    def test_marker_semantics_normalize_waypoint_portal_and_direction(self):
        text = (
            "向 __XUI_TOKEN_001__ 前往出口，取得 __XUI_TOKEN_002__，"
            "设置 __XUI_TOKEN_003__"
        )
        tokens = {
            "__XUI_TOKEN_001__": "(img:7)",
            "__XUI_TOKEN_002__": "(img:waypoint)",
            "__XUI_TOKEN_003__": "(img:portal)",
        }
        self.assertEqual(
            localize.restore_tokens(text, tokens),
            "沿 (img:7) 方向前往出口，激活 (img:waypoint)，开启 (img:portal)",
        )

    def test_direction_to_waypoint_is_not_rendered_as_obtaining_an_icon(self):
        text = "向 __XUI_TOKEN_001__ 取得 __XUI_TOKEN_002__"
        tokens = {
            "__XUI_TOKEN_001__": "(img:2)",
            "__XUI_TOKEN_002__": "(img:waypoint)",
        }
        self.assertEqual(
            localize.restore_tokens(text, tokens),
            "沿 (img:2) 方向前进，激活 (img:waypoint)",
        )

    def test_crafting_recipe_icon_uses_unlock_semantics(self):
        text = "取得 __XUI_TOKEN_001__"
        tokens = {"__XUI_TOKEN_001__": "(img:craft)"}
        self.assertEqual(
            localize.restore_tokens(text, tokens),
            "解锁 (img:craft) 工艺配方",
        )

    def test_wrapped_quest_label_can_have_distinct_meaning(self):
        original = localize._QUEST_LABELS
        try:
            localize._QUEST_LABELS = {"zh-CN": {"eye": "欲望之眼", "(eye)": "愤怒之眼"}}
            self.assertEqual(localize.localized_quest_token("(quest:eye)", "zh-CN"), "(quest:欲望之眼)")
            self.assertEqual(localize.localized_quest_token("(quest:(eye))", "zh-CN"), "(quest:(愤怒之眼))")
        finally:
            localize._QUEST_LABELS = original

    def test_reused_eye_label_uses_source_context(self):
        original = localize._QUEST_LABELS
        try:
            localize._QUEST_LABELS = {"zh-CN": {"(eye)": "愤怒之眼", "(eye_of_conquest)": "征服之眼"}}
            token = localize.localized_quest_token("(quest:(eye))", "zh-CN", "kill queen (quest:(eye))")
            self.assertEqual(token, "(quest:(征服之眼))")
        finally:
            localize._QUEST_LABELS = original

    def test_renderer_boundaries_stop_chinese_color_bleed(self):
        text = "__XUI_TOKEN_001__起点与 __XUI_TOKEN_002__黑渊危机位于对角"
        tokens = {"__XUI_TOKEN_001__": "(color:cc99ff)", "__XUI_TOKEN_002__": "arena:"}
        self.assertEqual(localize.restore_tokens(text, tokens), "(color:cc99ff)起点 与 arena:黑渊危机 位于对角")

    def test_quest_label_does_not_color_following_clause(self):
        text = "寻找 __XUI_TOKEN_001__，取得 __XUI_TOKEN_002__"
        tokens = {"__XUI_TOKEN_001__": "(quest:奴隶少女)", "__XUI_TOKEN_002__": "(quest:不灭之火)"}
        self.assertEqual(localize.restore_tokens(text, tokens), "寻找 (quest:奴隶少女) , 取得 (quest:不灭之火)")

    def test_duplicate_upstream_kill_controls_render_once(self):
        text = "找到并__XUI_TOKEN_001____XUI_TOKEN_002__ 德瑞"
        tokens = {
            "__XUI_TOKEN_001__": "击杀",
            "__XUI_TOKEN_002__": "击杀",
        }
        self.assertEqual(localize.restore_tokens(text, tokens), "找到并击杀 德瑞")


class GemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = localize.read_json(localize.ENGLISH / "[leveltracker] gems.json")
        cls.names = localize.load_gem_names()

    def test_complete_mapping_uses_bilingual_display_names(self):
        self.assertEqual(localize.gem_mapping_errors(self.source, self.names), [])
        self.assertEqual(self.names["absolution"], "赦罪（Absolution）")
        self.assertEqual(self.names["quicksilver flask"], "水银药剂（Quicksilver Flask）")
        self.assertEqual(self.names["dark pact"], "黑暗契约（Dark Pact）")

    def test_missing_gem_translation_is_reported(self):
        names = self.names.copy()
        names.pop("absolution")
        errors = localize.gem_mapping_errors(self.source, names)
        self.assertTrue(any("absolution" in error for error in errors))

    def test_build_preserves_data_and_adds_only_name(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "[leveltracker] gems.json"
            done, total = localize.build_gems(destination)
            built = localize.read_json(destination)
            validation = localize.validate_gems(destination)
        self.assertEqual((done, total), (470, 470))
        self.assertEqual(validation, [])
        self.assertEqual(set(built), set(self.source))
        for key, entry in self.source.items():
            if key.startswith("_"):
                self.assertEqual(built[key], entry)
            else:
                self.assertEqual(
                    {name: value for name, value in built[key].items() if name != "name"},
                    entry,
                )
                self.assertEqual(built[key]["name"], self.names[key])


class OfflinePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parents[2]

    def test_offline_entry_points_are_wired(self):
        main = (self.root / "Exile UI.ahk").read_text(encoding="utf-8-sig")
        launcher = (self.root / "Exile UI - Offline Preview.ahk").read_text(encoding="utf-8")
        module = (self.root / "modules" / "offline preview.ahk").read_text(encoding="utf-8")
        self.assertIn('arg = "--offline"', main)
        self.assertIn("OfflinePreview_Start()", main)
        self.assertIn("--offline", launcher)
        self.assertIn("data\\zh-CN\\[leveltracker] gems.json", module)
        self.assertIn("data\\zh-CN\\[leveltracker] guide labels.json", module)
        self.assertIn("data\\zh-CN\\[leveltracker] default guide.json", module)

    def test_offline_preview_data_is_localized(self):
        gems = localize.read_json(self.root / "data" / "zh-CN" / "[leveltracker] gems.json")
        guide = localize.read_json(self.root / "data" / "zh-CN" / "[leveltracker] default guide.json")
        self.assertEqual(gems["absolution"]["name"], "赦罪（Absolution）")
        self.assertEqual(len(guide), 10)


if __name__ == "__main__":
    unittest.main()
