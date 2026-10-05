import json
import re
import struct
import unittest
from pathlib import Path

from plugin_reader import records, scripts

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "build/Data"
PACKETS = json.loads((ROOT / "content/packets.json").read_text())
ORDER = ["Skyrim.esm", "EA_Core.esp", "EA_Dispatch.esp", "EA_Service.esp", "EA_Accounts.esp", "EA_Prototype.esp"]


class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugins = {name: list(records((DATA / name).read_bytes())) for name in ORDER[1:]}

    def test_no_overrides_esl_flags_or_deleted_records(self):
        allowed = {"TES4", "QUST", "BOOK", "MESG", "ACTI", "CONT"}
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
                        for prop in ("Orders", "Reports", "Responses", "PromptResponses", "LateResponses", "ExtensionRequests", "ApprovedExtensions", "DeniedExtensions", "SupplyIndex", "CaseIndex"):
                            self.assertEqual(len(props[prop]), len(PACKETS), prop)
                        supplies = sum("supply" in p for p in PACKETS)
                        cases = sum("case" in p for p in PACKETS)
                        for prop, count in (("Supplies", supplies), ("SupplyCounts", supplies), ("MissingMessages", supplies), ("CaseFiles", cases), ("ConclusionMenus", cases), ("SoundConclusions", cases), ("MisjudgedResponses", cases), ("FailureMessages", 10)):
                            self.assertEqual(len(props[prop]), count, prop)
                    if script == "EA_Accounts":
                        self.assertEqual(len(props["ClaimForms"]), 4)
                        self.assertEqual(len(props["Decisions"]), 4)

    def test_vmad_references_resolve_and_have_no_optional_masters(self):
        # Gold, the note inventory art, and each packet's named item.
        vanilla = {0xF, 0x97788} | {int(p["supply"]["form"], 16) for p in PACKETS if "supply" in p}
        for name, recs in self.plugins.items():
            masters = [v.rstrip(b"\0").decode() for n, v in recs[0].fields if n == "MAST"] + [name]
            for record in recs:
                for script, props in scripts(record.field("VMAD")):
                    source = (ROOT / "Data/Source/Scripts" / (script + ".psc")).read_text()
                    numeric = {n for t, n in re.findall(r"(?mi)^(Int(?:\[\])?) Property (\w+).*Auto$", source)}
                    for prop, value in props.items():
                        if prop in numeric:
                            continue
                        for form in value if isinstance(value, list) else [value]:
                            owner = masters[form >> 24]
                            local = form & 0xFFFFFF
                            if owner == "Skyrim.esm":
                                self.assertIn(local, vanilla)
                            else:
                                self.assertIn(local, [r.form_id & 0xFFFFFF for r in self.plugins[owner][1:]], (script, local))

    def test_books_are_readable_zero_value_documents(self):
        documents = json.loads((ROOT / "content/documents.json").read_text())
        for packet in PACKETS:
            documents += list(packet["documents"].values())
            if "case" in packet:
                documents += [packet["case"]["file"], packet["case"]["misjudged"]]
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
        types = {"Book": "BOOK", "Container": "CONT", "Message": "MESG"}
        for name, recs in self.plugins.items():
            masters = [v.rstrip(b"\0").decode() for n, v in recs[0].fields if n == "MAST"] + [name]
            for record in recs:
                for script, props in scripts(record.field("VMAD")):
                    source = (ROOT / "Data/Source/Scripts" / (script + ".psc")).read_text()
                    declared = dict((n, t.removesuffix("[]")) for t, n in re.findall(r"(?mi)^(\w+(?:\[\])?) Property (\w+).*Auto$", source))
                    for prop, value in props.items():
                        if declared[prop] in ("Form", "Int"):
                            continue
                        for form in value if isinstance(value, list) else [value]:
                            owner = masters[form >> 24]
                            target = next(r for r in self.plugins[owner][1:] if r.form_id & 0xFFFFFF == form & 0xFFFFFF)
                            if declared[prop].startswith("EA_"):
                                self.assertEqual(target.kind, "QUST")
                                self.assertIn(declared[prop], [s for s, _ in scripts(target.field("VMAD"))])
                            else:
                                self.assertEqual(target.kind, types[declared[prop]])

    def test_extension_papers_identify_each_assignment(self):
        for packet in PACKETS:
            for part in ("extensionRequest", "extensionApproved", "extensionDenied"):
                document = packet["documents"][part]
                self.assertIn(str(packet["assignment"]), document["title"])
                self.assertIn(str(packet["assignment"]), document["text"])

    def test_archives_do_not_respawn_and_quests_do_not_autostart(self):
        for recs in self.plugins.values():
            for record in recs:
                if record.kind == "CONT":
                    self.assertFalse(record.field("DATA")[0] & 2)
                if record.kind == "QUST":
                    flags = struct.unpack_from("<H", record.field("DNAM"))[0]
                    self.assertFalse(flags & 1)
                    self.assertIsNone(record.field("ALST"))

    def test_service_letter_arrays_keep_each_instruction_in_its_slot(self):
        recs = self.plugins['EA_Service.esp']
        quest = next(r for r in recs if r.editor_id == 'EA_ServiceQuest')
        props = dict(scripts(quest.field('VMAD')))['EA_Service']
        documents = {d['editorID']: d for p in PACKETS for d in list(p['documents'].values()) + ([p['case']['file'], p['case']['misjudged']] if 'case' in p else [])}
        for prop in ('Orders', 'Reports', 'Responses', 'PromptResponses', 'LateResponses', 'ExtensionRequests', 'ApprovedExtensions', 'DeniedExtensions'):
            for index, form in enumerate(props[prop]):
                record = next(r for r in recs if r.form_id == form)
                doc = documents[record.editor_id]
                self.assertIn(str(1001 + index), doc['title'] + doc['text'], (prop, index))
        supplied = [p for p in PACKETS if 'supply' in p]
        cases = [p for p in PACKETS if 'case' in p]
        self.assertEqual(props['SupplyIndex'], [supplied.index(p) if 'supply' in p else -1 for p in PACKETS])
        self.assertEqual(props['CaseIndex'], [cases.index(p) if 'case' in p else -1 for p in PACKETS])
        self.assertEqual(props['Supplies'], [int(p['supply']['form'], 16) for p in supplied])
        self.assertEqual(props['SupplyCounts'], [p['supply']['count'] for p in supplied])
        self.assertEqual(props['SoundConclusions'], [p['case']['sound'] for p in cases])
        for prop, part in (('CaseFiles', 'file'), ('MisjudgedResponses', 'misjudged')):
            for case, form in zip(cases, props[prop]):
                record = next(r for r in recs if r.form_id == form)
                self.assertEqual(record.editor_id, case['case'][part]['editorID'])
                self.assertIn(str(case['assignment']), documents[record.editor_id]['title'], prop)

    def test_case_papers_carry_their_assignment_and_menus_offer_three_conclusions(self):
        recs = self.plugins['EA_Service.esp']
        for packet in [p for p in PACKETS if 'case' in p]:
            with self.subTest(packet=packet['assignment']):
                papers = next(r for r in recs if r.editor_id == packet['case']['file']['editorID'])
                props = dict(scripts(papers.field('VMAD')))['EA_CaseFile']
                self.assertEqual(props['AssignmentID'], packet['assignment'])
                menu = next(r for r in recs if r.editor_id == packet['case']['menu']['editorID'])
                buttons = [v.rstrip(b'\0').decode() for n, v in menu.fields if n == 'ITXT']
                self.assertEqual(len(buttons), 4)
                self.assertEqual(buttons[-1], 'Cancel')
                self.assertIn(str(packet['assignment']), menu.field('DESC').decode())

    def test_quest_objectives_follow_packet_positions(self):
        quest = next(r for r in self.plugins['EA_Service.esp'] if r.editor_id == 'EA_ServiceQuest')
        indices = sorted(struct.unpack('<H', v)[0] for n, v in quest.fields if n == 'QOBJ')
        self.assertEqual(indices, sorted([100 + i for i in range(len(PACKETS))] + [200 + i for i in range(len(PACKETS))] + [300]))

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
