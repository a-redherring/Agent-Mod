import json
import re
import struct
import unittest
from pathlib import Path

from plugin_reader import records, scripts

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "build/Data"
CAMPAIGN = json.loads((ROOT / "content/campaign.json").read_text())
INSTRUCTIONS = CAMPAIGN["instructions"]
LETTERS = CAMPAIGN["letters"]
ORDER = ["Skyrim.esm", "EA_Core.esp", "EA_Dispatch.esp", "EA_Service.esp", "EA_Accounts.esp", "EA_Prototype.esp", "EA_Start.esp"]
# Vanilla forms the opening binds: the Northwatch faction and the starting dagger.
START_VANILLA = {0xC0637, 0x1397E}


# Condition kinds as EA_Service.Check numbers them.
KINDS = {kind: n for n, kind in enumerate(
    ("nights residenceDays visited deliver holds stageDone questBegun questNotBegun playerInFaction actorInFaction "
     "actorHolds actorDead actorAlive globalAtLeast earned level magic daysInPhase phaseWeight present "
     "questCompleted stageAtLeast").split(), 1)}


def all_conditions(source):
    return source["conditions"] + [source[k] for k in ("require", "alt") if k in source]


def campaign_vanilla():
    """Every Skyrim.esm form the campaign names: condition forms, enclosures, places and books."""
    forms = set()
    for source in INSTRUCTIONS + LETTERS:
        for c in all_conditions(source):
            if "plugin" in c:
                continue
            for key in ("form", "other"):
                if c.get(key, "LIST") != "LIST":
                    forms.add(int(c[key], 16))
        forms |= {int(f, 16) for f in source.get("enclosures", [])}
    forms |= {int(f, 16) for f in CAMPAIGN["packetBooks"] + CAMPAIGN["arcanaeum"]["books"]}
    forms |= {int(CAMPAIGN["places"]["inn"], 16)} | {int(f, 16) for f in CAMPAIGN["places"]["bounds"]}
    return forms


VANILLA = {0xF, 0x97788} | START_VANILLA | campaign_vanilla()


class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugins = {name: list(records((DATA / name).read_bytes())) for name in ORDER[1:]}

    def test_no_overrides_esl_flags_or_deleted_records(self):
        allowed = {"TES4", "QUST", "BOOK", "MESG", "ACTI", "CONT", "MISC", "FLST"}
        for name, recs in self.plugins.items():
            with self.subTest(plugin=name):
                header = recs[0]
                self.assertEqual(header.kind, "TES4")
                self.assertEqual(header.flags, 0)
                self.assertAlmostEqual(struct.unpack_from("<f", header.field("HEDR"))[0], 1.70, places=5)
                masters = [v.rstrip(b"\0").decode() for n, v in header.fields if n == "MAST"]
                self.assertEqual(masters, sorted(masters, key=ORDER.index))
                self.assertTrue(all(ORDER.index(m) < ORDER.index(name) for m in masters))
                seen = set()
                for record in recs[1:]:
                    self.assertIn(record.kind, allowed)
                    self.assertEqual(record.version, 44)
                    self.assertEqual(record.form_id >> 24, len(masters))
                    self.assertGreaterEqual(record.form_id & 0xFFFFFF, 0x800)
                    self.assertFalse(record.flags & 0x20)
                    self.assertNotIn(record.form_id, seen)
                    seen.add(record.form_id)
                    self.assertTrue(record.editor_id.startswith("EA_"))

    def test_vmad_properties_match_compiled_script_types(self):
        dynamic = {("EA_Core", "DebugEnabled"), ("EA_Dispatch", "Archive")}
        for name, recs in self.plugins.items():
            for record in recs:
                for script, props in scripts(record.field("VMAD")):
                    source = (ROOT / "Data/Source/Scripts" / (script + ".psc")).read_text()
                    declared = dict((n, t) for t, n in re.findall(r"(?mi)^(\w+(?:\[\])?) Property (\w+).*Auto$", source))
                    assembly = (DATA / "Scripts" / (script + ".pas")).read_text()
                    compiled = dict((n.lower(), t.lower()) for n, t in re.findall(r"\.property (\w+) (\S+) auto", assembly))
                    self.assertEqual({n.lower(): t.lower() for n, t in declared.items()}, compiled)
                    self.assertEqual(set(props) | {p for s, p in dynamic if s == script}, set(declared), (name, record.editor_id))
                    for prop, value in props.items():
                        self.assertEqual(isinstance(value, list), declared[prop].endswith("[]"), prop)
                        self.assertTrue(value, (script, prop))
                    if script == "EA_Service":
                        for prop in ("Orders", "Reports", "Replies", "AltReplies", "Phases", "CondStart", "CondCount", "RequireCond", "AltCond", "Weights", "AltWeights", "AltTrust", "NotYetMessages"):
                            self.assertEqual(len(props[prop]), len(INSTRUCTIONS), prop)
                        for prop in ("Letters", "LetterPhases", "LetterCondStart", "LetterCondCount", "LetterActions", "EnclosureStart", "EnclosureCount"):
                            self.assertEqual(len(props[prop]), len(LETTERS), prop)
                        conditions = len(props["CondKinds"])
                        for prop in ("CondForms", "CondOtherForms", "CondValues", "CondPlugins", "CondFormIDs"):
                            self.assertEqual(len(props[prop]), conditions, prop)
                        self.assertEqual(len(props["Enclosures"]), sum(len(l.get("enclosures", [])) for l in LETTERS))
                        self.assertEqual(len(props["FailureMessages"]), 3)
                    if script == "EA_Accounts":
                        self.assertEqual(len(props["ClaimForms"]), 4)
                        self.assertEqual(len(props["Decisions"]), 4)

    def test_vmad_references_resolve_and_have_no_optional_masters(self):
        for name, recs in self.plugins.items():
            masters = [v.rstrip(b"\0").decode() for n, v in recs[0].fields if n == "MAST"] + [name]
            for record in recs:
                for script, props in scripts(record.field("VMAD")):
                    source = (ROOT / "Data/Source/Scripts" / (script + ".psc")).read_text()
                    numeric = {n for t, n in re.findall(r"(?mi)^((?:Int|String)(?:\[\])?) Property (\w+).*Auto$", source)}
                    for prop, value in props.items():
                        if prop in numeric:
                            continue
                        for form in value if isinstance(value, list) else [value]:
                            if form == 0:
                                # Unused slots: a missing alternative reply, a condition with no form.
                                self.assertIn(prop, ("AltReplies", "CondForms", "CondOtherForms"), script)
                                continue
                            owner = masters[form >> 24]
                            local = form & 0xFFFFFF
                            if owner == "Skyrim.esm":
                                self.assertIn(local, VANILLA, (script, prop))
                            else:
                                self.assertIn(local, [r.form_id & 0xFFFFFF for r in self.plugins[owner][1:]], (script, local))

    def test_books_are_readable_zero_value_documents(self):
        documents = json.loads((ROOT / "content/documents.json").read_text())
        documents += json.loads((ROOT / "content/start.json").read_text())["documents"]
        for i in INSTRUCTIONS:
            documents += [i[k] for k in ("order", "report", "reply", "altReply") if k in i]
        documents += [l["letter"] for l in LETTERS] + [CAMPAIGN["wander"]]
        books = {r.editor_id: r for recs in self.plugins.values() for r in recs if r.kind == "BOOK"}
        self.assertEqual(len(books), len(documents))
        for doc in documents:
            record = books[doc["editorID"]]
            self.assertIn(doc["title"].encode(), record.field("FULL"))
            self.assertIn(b"$HandwrittenFont", record.field("DESC"))
            self.assertIsNotNone(record.field("INAM"))
            flags, kind, unused, teaches, price, weight = struct.unpack("<BBHiIf", record.field("DATA"))
            self.assertEqual(price, 0)
            self.assertEqual(weight, 0)

    def test_compiled_code_never_operates_on_one_temporary_twice(self):
        # Caprica v0.3.0 once compiled "CheckAll(..) == (pass == 0)" as "COMPAREEQ t0 t0 t0", always true.
        pattern = re.compile(r"\s*(COMPARE\w+|IADD|ISUBTRACT|FADD|FSUBTRACT|FMULTIPLY|STRCAT)\s+(\S+)\s+(::temp\d+)\s+\3\b")
        for path in sorted((DATA / "Scripts").glob("EA_*.pas")):
            for number, line in enumerate(path.read_text().splitlines(), 1):
                self.assertIsNone(pattern.match(line), f"{path.name}:{number}: {line.strip()}")

    def test_script_binary_targets_skyrim_and_is_not_empty(self):
        sources = list((ROOT / "Data/Source/Scripts").glob("EA_*.psc"))
        self.assertEqual(len(sources), len(list((DATA / "Scripts").glob("*.pex"))))
        for source in sources:
            binary = (DATA / "Scripts" / (source.stem + ".pex")).read_bytes()
            self.assertEqual(binary[:8], bytes.fromhex("fa57c0de03020001"))
            self.assertGreater(len(binary), 100)

    def test_core_has_only_official_master(self):
        masters = [v.rstrip(b"\0").decode() for n, v in self.plugins["EA_Core.esp"][0].fields if n == "MAST"]
        self.assertEqual(masters, ["Skyrim.esm"])

    def test_record_identifiers_match_persistent_contract(self):
        expected = json.loads((ROOT / "content/record-ids.json").read_text())
        actual = json.loads((ROOT / "build/record-map.json").read_text())
        self.assertEqual(actual, expected)
        binary_map = {r.editor_id: f"{r.form_id & 0xFFFFFF:06X}:{name}" for name, recs in self.plugins.items() for r in recs[1:]}
        self.assertEqual(binary_map, expected)

    def test_vmad_targets_have_the_required_record_and_script_types(self):
        types = {"Book": "BOOK", "Container": "CONT", "Message": "MESG", "Activator": "ACTI", "MiscObject": "MISC", "FormList": "FLST"}
        for name, recs in self.plugins.items():
            masters = [v.rstrip(b"\0").decode() for n, v in recs[0].fields if n == "MAST"] + [name]
            for record in recs:
                for script, props in scripts(record.field("VMAD")):
                    source = (ROOT / "Data/Source/Scripts" / (script + ".psc")).read_text()
                    declared = dict((n, t.removesuffix("[]")) for t, n in re.findall(r"(?mi)^(\w+(?:\[\])?) Property (\w+).*Auto$", source))
                    for prop, value in props.items():
                        if declared[prop] in ("Form", "Int", "String"):
                            continue
                        for form in value if isinstance(value, list) else [value]:
                            if form == 0:
                                continue
                            owner = masters[form >> 24]
                            if owner == "Skyrim.esm":
                                self.assertIn(form & 0xFFFFFF, VANILLA, (script, prop))
                                continue
                            target = next(r for r in self.plugins[owner][1:] if r.form_id & 0xFFFFFF == form & 0xFFFFFF)
                            if declared[prop].startswith("EA_"):
                                self.assertEqual(target.kind, "QUST")
                                self.assertIn(declared[prop], [s for s, _ in scripts(target.field("VMAD"))])
                            else:
                                self.assertEqual(target.kind, types[declared[prop]])

    def test_archives_do_not_respawn_and_quests_do_not_autostart(self):
        for recs in self.plugins.values():
            for record in recs:
                if record.kind == "CONT":
                    self.assertFalse(record.field("DATA")[0] & 2)
                if record.kind == "QUST":
                    flags = struct.unpack_from("<H", record.field("DNAM"))[0]
                    self.assertFalse(flags & 1)
                    if record.editor_id not in ("EA_StartQuest", "EA_ServiceQuest"):
                        self.assertIsNone(record.field("ALST"))

    def test_service_arrays_keep_each_instruction_and_letter_in_its_slot(self):
        recs = self.plugins["EA_Service.esp"]
        by_id = {r.form_id: r.editor_id for r in recs}
        quest = next(r for r in recs if r.editor_id == "EA_ServiceQuest")
        props = dict(scripts(quest.field("VMAD")))["EA_Service"]
        for index, i in enumerate(INSTRUCTIONS):
            with self.subTest(instruction=i["key"]):
                self.assertEqual(by_id[props["Orders"][index]], i["order"]["editorID"])
                self.assertEqual(by_id[props["Reports"][index]], i["report"]["editorID"])
                self.assertEqual(by_id[props["Replies"][index]], i["reply"]["editorID"])
                self.assertEqual(by_id.get(props["AltReplies"][index]), i["altReply"]["editorID"] if "altReply" in i else None)
                self.assertEqual(by_id[props["NotYetMessages"][index]], i["notYet"]["editorID"])
                self.assertEqual(props["Phases"][index], i["phase"])
                self.assertEqual(props["CondCount"][index], len(i["conditions"]))
                start = props["CondStart"][index]
                self.assertEqual(props["CondKinds"][start:start + len(i["conditions"])], [KINDS[c["kind"]] for c in i["conditions"]])
        for index, l in enumerate(LETTERS):
            with self.subTest(letter=l["key"]):
                self.assertEqual(by_id[props["Letters"][index]], l["letter"]["editorID"])
                self.assertEqual(props["LetterPhases"][index], l["phase"])
                self.assertEqual(props["LetterActions"][index], l.get("action", 0))
                self.assertEqual(props["LetterCondCount"][index], len(l["conditions"]))
                self.assertEqual(props["EnclosureCount"][index], len(l.get("enclosures", [])))
        self.assertEqual(by_id[props["WanderLetter"]], CAMPAIGN["wander"]["editorID"])
        self.assertEqual(props["Inn"], int(CAMPAIGN["places"]["inn"], 16))
        self.assertEqual(props["Bounds"], [int(f, 16) for f in CAMPAIGN["places"]["bounds"]])
        self.assertEqual((props["AdvanceOperation"], props["RemovalOperation"]), (CAMPAIGN["operations"]["advance"], CAMPAIGN["operations"]["removal"]))
        plugins = {(c["plugin"], c["local"]) for s in INSTRUCTIONS + LETTERS for c in all_conditions(s) if "plugin" in c}
        self.assertEqual({(p, f) for p, f in zip(props["CondPlugins"], props["CondFormIDs"]) if p}, plugins, "optional plugins are never masters")

    def test_arcanaeum_list_holds_the_named_books(self):
        recs = self.plugins["EA_Service.esp"]
        flst = next(r for r in recs if r.kind == "FLST")
        self.assertEqual(flst.editor_id, CAMPAIGN["arcanaeum"]["editorID"])
        self.assertEqual([struct.unpack("<I", v)[0] for n, v in flst.fields if n == "LNAM"], [int(b, 16) for b in CAMPAIGN["arcanaeum"]["books"]])

    def test_service_player_alias_reports_arrivals(self):
        quest = next(r for r in self.plugins['EA_Service.esp'] if r.editor_id == 'EA_ServiceQuest')
        self.assertEqual(struct.unpack('<I', quest.field('ALST'))[0], 0)
        self.assertEqual(struct.unpack('<I', quest.field('ALFR'))[0], 0x14, 'the player')
        self.assertIn(b'EA_ServicePlayer', quest.field('VMAD'))
        source = (ROOT / 'Data/Source/Scripts/EA_ServicePlayer.psc').read_text()
        for event in ('Event OnLocationChange', 'Event OnSleepStop', 'Event OnPlayerLoadGame'):
            self.assertIn(event, source)

    def test_start_quest_is_a_start_up_stage_with_northwatch_aliases_and_a_real_fragment(self):
        quest = next(r for r in self.plugins["EA_Start.esp"] if r.editor_id == "EA_StartQuest")
        stages = {struct.unpack_from("<H", v)[0]: v[2] for n, v in quest.fields if n == "INDX"}
        self.assertEqual(stages, {10: 2, 20: 0}, "only stage 10 is the start-up stage")
        self.assertEqual([struct.unpack("<I", v)[0] for n, v in quest.fields if n in ("ALLS", "ALST")], [0, 1, 2])
        field = lambda kind: struct.unpack("<I", quest.field(kind))[0]
        self.assertEqual(field("ALFL"), 0x019285, "NorthwatchKeepLocation in Skyrim.esm")
        self.assertEqual(field("ALRT"), 0x10F63C, "MapMarkerRefType")
        self.assertEqual(field("ALFA"), 0, "the marker is found in the Northwatch alias")
        self.assertEqual(field("ALFR"), 0x14, "the player")
        self.assertEqual(struct.unpack_from("<H", quest.field("DNAM"))[0] & 1, 0, "Alternate Perspective starts it")
        vmad = quest.field("VMAD")
        self.assertTrue(vmad.endswith(b"\x0a\x00EA_Opening\x0b\x00Fragment_10\x00\x00"))
        self.assertIn("Function Fragment_10()", (ROOT / "Data/Source/Scripts/EA_Opening.psc").read_text())
        registration = json.loads((DATA / "SKSE/AlternatePerspective/ElenwenAgent.json").read_text())
        self.assertEqual([(e["mod"], int(e["id"], 16)) for e in registration], [("EA_Start.esp", quest.form_id & 0xFFFFFF)])

    def test_quest_objectives_follow_instruction_positions(self):
        quest = next(r for r in self.plugins['EA_Service.esp'] if r.editor_id == 'EA_ServiceQuest')
        indices = sorted(struct.unpack('<H', v)[0] for n, v in quest.fields if n == 'QOBJ')
        self.assertEqual(indices, [100 + i for i in range(len(INSTRUCTIONS))] + [200 + i for i in range(len(INSTRUCTIONS))])

    def test_menus_and_numeric_status_fit_the_native_message_interface(self):
        for recs in self.plugins.values():
            for record in recs:
                if record.kind != 'MESG':
                    continue
                buttons = [v.rstrip(b'\0').decode() for n, v in record.fields if n == 'ITXT']
                self.assertGreaterEqual(len(buttons), 1, record.editor_id)
                self.assertLessEqual(len(buttons), 9, record.editor_id)
                self.assertLessEqual(record.field('DESC').count(b'%'), 9, record.editor_id)
                self.assertIn(buttons[-1], ('Close', 'Cancel', 'Leave'), record.editor_id)


if __name__ == "__main__":
    unittest.main()
