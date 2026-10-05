"""Authored-content rules from Continuation 01, sections 5-6, checked on the source JSON."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKETS = json.loads((ROOT / "content/packets.json").read_text())
DOCUMENTS = json.loads((ROOT / "content/documents.json").read_text())
RETIRED = json.loads((ROOT / "content/retired-records.json").read_text())
RECORDS = json.loads((ROOT / "content/record-ids.json").read_text())
PARTS = ("order", "report", "response", "prompt", "late", "extensionRequest", "extensionApproved", "extensionDenied")
# Elenwen's own letters, as opposed to the officer's filed papers and the copied case papers.
LETTERS = ("order", "response", "prompt", "late", "extensionApproved", "extensionDenied")
# Generic or common items the continuation rules out as a principal service loop (section 2, decision 3),
# plus vanilla base objects reserved by unrelated quests (section 5.5). Skyrim.esm FormIDs.
GENERIC = {0x3133B: "Alto Wine", 0xC5349: "Alto Wine (variant)", 0x3133C: "Wine", 0xC5348: "Wine (variant)",
           0x6F993: "Firewood", 0x4B0BA: "Wheat", 0x77E1C: "Blue Mountain Flower", 0x800E4: "Leather Strips",
           0x71CF3: "Iron Ore", 0x34C5E: "Ale", 0x34C5D: "Nord Mead"}
QUEST_ITEMS = {0x1895F: "Firebrand Wine", 0xF257E: "MS14 Alto Wine", 0xB91D7: "WEDL03 Cyrodilic Brandy",
               0x9380D: "Whiterun quest ale", 0x107A8A: "MQ101 Juniper Mead", 0x555E8: "Dragon Bridge mead"}
# Section 6.3: no contemporary corporate jargon or spy-film cliche. A starting list; Phase C extends it.
PROHIBITED = ("deliverable", "circle back", "touch base", "going forward", "synergy", "stakeholder", "bandwidth",
              "performance review", "team player", "licence to kill", "license to kill", "eyes only", "burn notice",
              "double-oh", "agent of the thalmor", "my dear", "darling", "sweetheart", "okay", "ok.")


def all_documents():
    for packet in PACKETS:
        yield from packet["documents"].values()
        if "case" in packet:
            yield packet["case"]["file"]
            yield packet["case"]["misjudged"]
    yield from DOCUMENTS


class ContentTests(unittest.TestCase):
    def test_pool_meets_the_phase_b_exit_size_and_numbering(self):
        self.assertGreaterEqual(len(PACKETS), 10)
        self.assertLessEqual(len(PACKETS), 16)
        self.assertEqual([p["assignment"] for p in PACKETS], list(range(1001, 1001 + len(PACKETS))))
        self.assertEqual(len({p["key"] for p in PACKETS}), len(PACKETS))

    def test_every_packet_is_complete_and_identifies_itself(self):
        for packet in PACKETS:
            with self.subTest(packet=packet["assignment"]):
                self.assertEqual(set(packet["documents"]), set(PARTS))
                self.assertTrue(packet["objective"])
                number = str(packet["assignment"])
                for part in PARTS:
                    self.assertIn(number, packet["documents"][part]["title"] + packet["documents"][part]["text"], part)
                self.assertIn("ten days", packet["documents"]["order"]["text"].lower())
                self.assertTrue("supply" in packet or "case" in packet or packet["assignment"] == 1001,
                                "a packet must rest on a named item or case papers")

    def test_named_items_are_specific_distinct_and_not_reserved_by_other_quests(self):
        forms = [int(p["supply"]["form"], 16) for p in PACKETS if "supply" in p]
        self.assertEqual(len(forms), len(set(forms)), "no two packets may ask for the same item")
        for packet in [p for p in PACKETS if "supply" in p]:
            with self.subTest(packet=packet["assignment"]):
                form = int(packet["supply"]["form"], 16)
                self.assertNotIn(form, GENERIC)
                self.assertNotIn(form, QUEST_ITEMS)
                self.assertGreaterEqual(packet["supply"]["count"], 1)
                self.assertLessEqual(packet["supply"]["count"], 6)
                self.assertIn("%.0f", packet["supply"]["message"]["text"])
                self.assertIn("Nothing has been taken", packet["supply"]["message"]["text"])

    def test_case_packets_offer_three_conclusions_and_distinct_outcomes(self):
        for packet in [p for p in PACKETS if "case" in p]:
            with self.subTest(packet=packet["assignment"]):
                case = packet["case"]
                self.assertIn(case["sound"], (0, 1, 2))
                self.assertEqual(len(case["menu"]["buttons"]), 4)
                self.assertEqual(case["menu"]["buttons"][-1], "Cancel")
                self.assertEqual(len(set(case["menu"]["buttons"])), 4)
                self.assertTrue(all(len(b) <= 40 for b in case["menu"]["buttons"]))
                self.assertIn(str(packet["assignment"]), case["file"]["title"])
                self.assertIn("conclusion", packet["documents"]["order"]["text"])
                self.assertNotEqual(case["misjudged"]["text"], packet["documents"]["response"]["text"])
                self.assertIn("on your record", case["misjudged"]["text"])

    def test_reply_variants_are_distinct(self):
        texts = [d["text"] for d in all_documents()]
        self.assertEqual(len(texts), len(set(texts)), "no two documents may share text")
        for packet in PACKETS:
            replies = [packet["documents"][k]["text"] for k in ("response", "prompt", "late")]
            self.assertEqual(len(set(replies)), 3, packet["assignment"])
            self.assertIn("on your record", packet["documents"]["late"]["text"])

    def test_elenwen_letters_are_signed_and_economical(self):
        for packet in PACKETS:
            for part in LETTERS:
                with self.subTest(packet=packet["assignment"], part=part):
                    text = packet["documents"][part]["text"]
                    self.assertTrue(text.endswith("\n\nElenwen"), "letters close without rhetoric, signed")
                    self.assertLessEqual(len(text), 700 if part == "order" else 300)
            if "case" in packet:
                self.assertTrue(packet["case"]["misjudged"]["text"].endswith("\n\nElenwen"))
                self.assertLessEqual(len(packet["case"]["misjudged"]["text"]), 300)
                self.assertLessEqual(len(packet["case"]["file"]["text"]), 800)
                self.assertNotIn("Elenwen", packet["case"]["file"]["text"], "case papers are copies, not her letters")

    def test_filed_papers_are_the_officers_and_unsigned_by_elenwen(self):
        for packet in PACKETS:
            for part in ("report", "extensionRequest"):
                text = packet["documents"][part]["text"]
                self.assertNotIn("Elenwen", text)
                self.assertTrue(text.endswith("Filed by secure dispatch."), (packet["assignment"], part))

    def test_no_prohibited_phrasing(self):
        for document in all_documents():
            text = (document["title"] + " " + document["text"]).lower()
            for phrase in PROHIBITED:
                self.assertIsNone(re.search(r"\b" + re.escape(phrase), text), (document["editorID"], phrase))
            self.assertNotIn("!", document["text"], document["editorID"])

    def test_retired_records_are_not_reused(self):
        live = set(RECORDS.values())
        for editor_id, key in RETIRED.items():
            self.assertNotIn(editor_id, RECORDS)
            self.assertNotIn(key, live, editor_id)


if __name__ == "__main__":
    unittest.main()
