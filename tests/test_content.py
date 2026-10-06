"""Authored-content rules for the campaign letters (campaign doc, "Letter tradecraft"), checked on the source JSON."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = json.loads((ROOT / "content/campaign.json").read_text())
START = json.loads((ROOT / "content/start.json").read_text())
DOCUMENTS = json.loads((ROOT / "content/documents.json").read_text())
RETIRED = json.loads((ROOT / "content/retired-records.json").read_text())
RECORDS = json.loads((ROOT / "content/record-ids.json").read_text())
# Rules 1-3: no names or institutions in clear, in either direction.
IN_CLEAR = ("Cotta", "Elenwen", "Embassy", "Thalmor", "Dominion", "Justiciar", "First Emissary", "Concordat",
            "Northwatch", "Delphine", "Ancano", "Madanach", "Ogmund", "Sanyon", "Jenassa", "Ondolemar")
# Rule 11: papers meant to be official keep their formal style.
OFFICIAL = {"EA_CivilianPapers", "EA_ConditionalRelease", "EA_SealedPacket"}
# MQ101 (Helgen), MQ201 (Diplomatic Immunity): no condition may depend on the main quest's opening.
MAIN_QUEST = {0x3372B, 0x35D5F}
PROHIBITED = ("deliverable", "circle back", "touch base", "going forward", "synergy", "stakeholder", "bandwidth",
              "performance review", "team player", "licence to kill", "license to kill", "eyes only", "burn notice",
              "double-oh", "agent of the thalmor", "my dear", "darling", "sweetheart", "okay", "ok.")


def her_letters():
    for i in CAMPAIGN["instructions"]:
        yield i["order"]
        yield i["reply"]
        if "altReply" in i:
            yield i["altReply"]
    for letter in CAMPAIGN["letters"]:
        yield letter["letter"]
    yield CAMPAIGN["wander"]
    yield next(d for d in START["documents"] if d["editorID"] == "EA_ArrivalLetter")


def his_reports():
    for i in CAMPAIGN["instructions"]:
        yield i["report"]


def all_documents():
    yield from her_letters()
    yield from his_reports()
    yield from DOCUMENTS
    yield from (d for d in START["documents"] if d["editorID"] != "EA_ArrivalLetter")


class ContentTests(unittest.TestCase):
    def test_instructions_are_numbered_keyed_and_phased(self):
        instructions = CAMPAIGN["instructions"]
        self.assertEqual([i["assignment"] for i in instructions], list(range(2001, 2001 + len(instructions))))
        self.assertEqual(len({i["key"] for i in instructions}), len(instructions))
        self.assertLessEqual(len(instructions), 32, "Core holds thirty-two open campaign assignments")
        phases = [i["phase"] for i in instructions]
        self.assertEqual(phases, sorted(phases))
        self.assertEqual(set(phases), {1, 2, 4}, "phase 3 is the interval with no assignments")
        for i in instructions:
            with self.subTest(instruction=i["key"]):
                self.assertTrue(i["objective"])
                self.assertTrue(i["conditions"], "every instruction rests on something the game records")
                self.assertIn(str(i["assignment"]), i["report"]["text"])

    def test_letters_open_with_his_initial_and_close_with_hers(self):
        for doc in her_letters():
            with self.subTest(doc=doc["editorID"]):
                self.assertTrue(doc["text"].startswith("C.,\n\n"))
                self.assertTrue(doc["text"].endswith("\n\n— E."))
                self.assertNotIn("By my hand and seal", doc["text"])
        for doc in his_reports():
            with self.subTest(doc=doc["editorID"]):
                self.assertTrue(doc["text"].endswith("\n\n— C."))

    def test_nothing_is_named_in_clear(self):
        for doc in list(her_letters()) + list(his_reports()):
            for name in IN_CLEAR:
                with self.subTest(doc=doc["editorID"], name=name):
                    self.assertNotIn(name.lower(), (doc.get("title", "") + " " + doc["text"]).lower())

    def test_only_official_papers_carry_her_formal_signature(self):
        for doc in all_documents():
            if "By my hand and seal" in doc["text"]:
                self.assertIn(doc["editorID"], OFFICIAL)

    def test_replies_keep_the_meaning_to_themselves(self):
        # Rule 5: she acknowledges, restricts or redirects; she does not explain what he found.
        for i in CAMPAIGN["instructions"]:
            for part in ("reply", "altReply"):
                if part in i:
                    text = i[part]["text"].lower()
                    for explaining in ("which means", "this means", "the reason", "conclusion"):
                        self.assertNotIn(explaining, text, (i["key"], part))

    def test_alternative_outcomes_carry_their_own_reply(self):
        for i in CAMPAIGN["instructions"]:
            if i.get("altWeight") or i.get("altTrust"):
                self.assertIn("altReply", i, i["key"])
                self.assertNotEqual(i["altReply"]["text"], i["reply"]["text"])

    def test_not_yet_messages_file_nothing(self):
        for i in CAMPAIGN["instructions"]:
            self.assertIn("Nothing has been filed", i["notYet"]["text"], i["key"])

    def test_every_text_is_distinct(self):
        texts = [d["text"] for d in all_documents()] + [i["notYet"]["text"] for i in CAMPAIGN["instructions"]]
        self.assertEqual(len(texts), len(set(texts)), "no two documents may share text")

    def test_no_prohibited_phrasing(self):
        for document in all_documents():
            text = (document.get("title", "") + " " + document["text"]).lower()
            for phrase in PROHIBITED:
                self.assertIsNone(re.search(r"\b" + re.escape(phrase), text), (document["editorID"], phrase))

    def test_conditions_never_wait_on_the_main_quest_opening(self):
        for source in CAMPAIGN["instructions"] + CAMPAIGN["letters"]:
            for c in source["conditions"]:
                if c.get("form", "LIST") != "LIST" and "plugin" not in c and c["kind"] != "questNotBegun":
                    self.assertNotIn(int(c["form"], 16), MAIN_QUEST, source["key"])

    def test_letters_alter_the_campaign_only_by_known_actions(self):
        for letter in CAMPAIGN["letters"]:
            self.assertIn(letter.get("action", 0), (0, 1, 2, 3), letter["key"])
        actions = [l.get("action", 0) for l in CAMPAIGN["letters"]]
        self.assertEqual(actions.count(2), 1, "one release")
        self.assertEqual(actions.count(3), 1, "one removal order")

    def test_arcanaeum_list_is_distinct_and_matches_the_library_instruction(self):
        books = CAMPAIGN["arcanaeum"]["books"]
        self.assertEqual(len(books), len(set(books)))
        library = next(i for i in CAMPAIGN["instructions"] if i["key"] == "Library")
        self.assertTrue(any(c["kind"] == "deliver" for c in library["conditions"]))

    def test_retired_records_are_not_reused(self):
        live = set(RECORDS.values())
        for editor_id, key in RETIRED.items():
            self.assertNotIn(editor_id, RECORDS)
            self.assertNotIn(key, live, editor_id)


if __name__ == "__main__":
    unittest.main()
