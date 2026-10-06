"""Small test interpreter for Caprica's *compiled* Skyrim assembly.

Runs the shipped scripts' instructions, not a second implementation of EA rules.
Only the emitted opcode subset is supported; unknown instructions fail closed.
Native inventory, clock, menus, and quest calls are deterministic test doubles.
This does not emulate the game's VM scheduling, save format, physics, or UI.
"""
from __future__ import annotations

import copy
import json
import re
import shlex
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path


def literal(token):
    if token.startswith('"'):
        return bytes(token[1:-1], "utf8").decode("unicode_escape")
    if token.lower() in ("true", "false", "none"):
        return {"true": True, "false": False, "none": None}[token.lower()]
    try:
        return float(token) if "." in token else int(token)
    except ValueError:
        raise KeyError(token)


def default(kind):
    return {"int": 0, "float": 0.0, "bool": False, "string": ""}.get(kind.lower())


@dataclass
class Function:
    params: list
    types: dict
    code: list
    labels: dict


class Script:
    def __init__(self, path):
        text = path.read_text()
        self.name, self.parent = re.search(r"\.object (\S+) (\S+)", text).groups()
        self.variables = {}
        self.types = {}
        self.functions = {}
        for name, kind, body in re.findall(r"\.variable (\S+) (\S+)\n(.*?)\.endVariable", text, re.S):
            self.types[name.lower()] = kind
            initial = re.search(r"\.initialValue (.*)", body).group(1).strip()
            self.variables[name.lower()] = literal(initial)
        for state_name, body in re.findall(r"\.state(?:[ \t]+([^\n]*))?\n(.*?)\.endState\b", text, re.S):
            for name, func in re.findall(r"\.function (\S+)[^\n]*\n(.*?)\.endFunction", body, re.S):
                params = re.findall(r"\.param (\S+) (\S+)", func)
                types = dict((n.lower(), t) for n, t in re.findall(r"\.(?:local|param) (\S+) (\S+)", func))
                code = []
                labels = {}
                source = re.search(r"\.code\n(.*?)\.endCode", func, re.S).group(1)
                for line in source.splitlines():
                    line = line.split(" ;@line")[0].strip()
                    if not line:
                        continue
                    if line.endswith(":"):
                        labels[line[:-1]] = len(code)
                    else:
                        code.append(shlex.split(line, posix=False))
                self.functions[(state_name.strip().lower(), name.lower())] = Function(params, types, code, labels)


@dataclass(eq=False)
class Inventory:
    """A container or placed reference. The player and NPCs are one, with factions and a position."""
    items: Counter = field(default_factory=Counter)
    factions: set = field(default_factory=set)
    at: object = None
    enabled: bool = True
    deleted: bool = False
    base: object = None
    dead: bool = False
    level: int = 1
    skills: dict = field(default_factory=dict)
    location: object = None


@dataclass(eq=False)
class FormList:
    forms: list


@dataclass(eq=False)
class Global:
    value: float = 0.0


@dataclass(eq=False)
class Alias:
    reference: object = None


@dataclass(eq=False)
class Place:
    """A vanilla Location; parent models Location.IsChild."""
    name: str
    parent: object = None


@dataclass(eq=False)
class VanillaQuest:
    """A vanilla quest the scripts only read."""
    name: str
    running: bool = False
    completed: bool = False
    stage: int = 0
    done: set = field(default_factory=set)


@dataclass(eq=False)
class Menu:
    choices: deque = field(default_factory=deque)
    shown: list = field(default_factory=list)


class Instance:
    def __init__(self, vm, script):
        self.vm = vm
        self.script = script
        self.vars = copy.deepcopy(vm.scripts[script.lower()].variables)
        # Skyrim supplies this variable implicitly; Caprica need not declare it.
        self.vars["::state"] = ""
        self.timer = None
        self.update = None
        self.stages = []
        self.aliases = {}
        self.objectives = {}
        self.running = False
        self.can_start = True
        # A script on a placed object is also that object; its reference natives act here.
        self.ref = Inventory()

    def prop(self, name, value):
        self.vars["::" + name.lower() + "_var"] = value
        return self

    def call(self, function, *args):
        return self.vm.call(self, function, list(args))


class VM:
    def __init__(self, directory):
        self.scripts = {p.stem.lower(): Script(p) for p in Path(directory).glob("EA_*.pas")}
        if not self.scripts:
            raise RuntimeError("Compile scripts with --dump-asm before running tests")
        self.day = 1.0
        self.player = Inventory()
        self.notifications = []
        self.traces = []
        self.stats = Counter()
        self.activations = []
        # Forms in optional plugins, keyed by (file, local ID); absent plugins return None.
        self.plugins = {}

    def instance(self, script):
        return Instance(self, script)

    def call(self, obj, method, args):
        name = method.lower()
        if isinstance(obj, Inventory):
            if name == "getitemcount":
                return obj.items[args[0]]
            if name == "isdead":
                return obj.dead
            if name == "getlevel":
                return obj.level
            if name == "getbaseactorvalue":
                return float(obj.skills.get(args[0], 15))
            if name == "getcurrentlocation":
                return obj.location
            if name == "additem":
                assert args[1] >= 0
                obj.items[args[0]] += args[1]
                return
            if name == "removeitem":
                assert 0 <= args[1] <= obj.items[args[0]], "Inventory underflow"
                obj.items[args[0]] -= args[1]
                if len(args) > 3 and args[3] is not None:
                    args[3].items[args[0]] += args[1]
                return
            if name == "placeatme":
                return Inventory(base=args[0], at=obj)
            if name == "moveto":
                obj.at = args[0]
                return
            if name == "addtofaction":
                obj.factions.add(args[0])
                return
            if name == "removefromfaction":
                obj.factions.discard(args[0])
                return
            if name == "isinfaction":
                return args[0] in obj.factions
            if name == "getdistance":
                # Distance is 0 at the reference itself, otherwise "far"; tests set positions explicitly.
                return 0.0 if obj.at is args[0] or obj is args[0] else 100000.0
            if name in ("disable", "enable"):
                obj.enabled = name == "enable"
                return
            if name == "delete":
                obj.deleted = True
                return
            if name == "activate":
                self.activations.append((obj, args[0]))
                return True
            if name == "stopcombatalarm":
                return
        if isinstance(obj, Alias) and name == "getreference":
            return obj.reference
        if isinstance(obj, Place) and name == "ischild":
            parent = obj.parent
            while parent is not None:
                if parent is args[0]:
                    return True
                parent = parent.parent
            return False
        if isinstance(obj, VanillaQuest):
            if name == "isrunning":
                return obj.running
            if name == "iscompleted":
                return obj.completed
            if name == "getstage":
                return obj.stage
            if name == "getstagedone":
                return args[0] in obj.done
        if isinstance(obj, FormList):
            if name == "getsize":
                return len(obj.forms)
            if name == "getat":
                return obj.forms[args[0]]
        if isinstance(obj, Global) and name == "getvalue":
            return obj.value
        if isinstance(obj, Menu) and name == "show":
            obj.shown.append(args)
            return obj.choices.popleft() if obj.choices else 0
        if not isinstance(obj, Instance):
            raise RuntimeError(f"Unsupported native call: {obj!r}.{method}")
        if name in ("placeatme", "disable", "enable", "delete", "moveto", "getdistance"):
            return self.call(obj.ref, method, args)
        if name in ("onbeginstate", "onendstate"):
            return
        if name == "start":
            if obj.running or not obj.can_start:
                return False
            obj.running = True
            return True
        if name == "isrunning":
            return obj.running
        if name == "registerforsleep":
            obj.sleeping = True
            return
        if name == "registerforsingleupdate":
            obj.update = args[0]
            return
        if name == "setstage":
            obj.stages.append(args[0])
            return True
        if name == "getstage":
            return obj.stages[-1] if obj.stages else 0
        if name == "getalias":
            return obj.aliases.get(args[0])
        if name == "registerforsingleupdategametime":
            obj.timer = self.day + args[0] / 24
            return
        if name == "unregisterforupdategametime":
            obj.timer = None
            return
        if name in ("setobjectivecompleted", "setobjectivedisplayed"):
            obj.objectives[(name, args[0])] = args[1]
            return
        state = obj.vars.get("::state", "").lower()
        script = self.scripts[obj.script.lower()]
        func = script.functions.get((state, name), script.functions.get(("", name)))
        while func is None and script.parent.lower() in self.scripts:
            script = self.scripts[script.parent.lower()]
            func = script.functions.get((state, name), script.functions.get(("", name)))
        if func is None:
            raise RuntimeError(f"Missing function {obj.script}.{method}")
        if len(args) != len(func.params):
            raise TypeError(f"{method}: expected {len(func.params)} parameters, got {len(args)}")
        local = {k: default(v) for k, v in func.types.items()}
        local.update((n.lower(), a) for (n, _), a in zip(func.params, args))
        local["self"] = obj

        def get(token):
            key = token.lower()
            if key in local:
                return local[key]
            if key in obj.vars:
                return obj.vars[key]
            return literal(token)

        def put(token, value):
            key = token.lower()
            if key in obj.vars:
                obj.vars[key] = value
            else:
                local[key] = value

        types = self.scripts[obj.script.lower()].types | func.types
        pc = 0
        steps = 0
        while pc < len(func.code):
            steps += 1
            if steps > 100000:
                raise RuntimeError("Instruction budget exceeded")
            op, *a = func.code[pc]
            pc += 1
            if op == "RETURN":
                return get(a[0])
            if op == "ASSIGN":
                put(a[0], get(a[1]))
            elif op == "NOT":
                put(a[0], not get(a[1]))
            elif op == "CAST":
                value = get(a[1])
                kind = types[a[0].lower()].lower()
                convert = {"int": int, "float": float, "bool": bool, "string": str}.get(kind)
                if convert:
                    put(a[0], convert(value))
                elif kind == "formlist":
                    put(a[0], value if isinstance(value, FormList) else None)
                else:
                    put(a[0], value)
            elif op == "ARRAYCREATE":
                kind = types[a[0].lower()][:-2]
                put(a[0], [default(kind) for _ in range(get(a[1]))])
            elif op == "ARRAYLENGTH":
                put(a[0], len(get(a[1])))
            elif op == "ARRAYGETELEMENT":
                assert get(a[2]) >= 0, "Negative array index"
                put(a[0], get(a[1])[get(a[2])])
            elif op == "ARRAYSETELEMENT":
                assert get(a[1]) >= 0, "Negative array index"
                get(a[0])[get(a[1])] = get(a[2])
            elif op in ("JUMP", "JUMPF", "JUMPT"):
                if op == "JUMP" or bool(get(a[0])) == (op == "JUMPT"):
                    pc = func.labels[a[-1]]
            elif op == "CALLMETHOD":
                put(a[2], self.call(get(a[1]), a[0], [get(x) for x in a[3:]]))
            elif op == "CALLSTATIC":
                target = (a[0] + "." + a[1]).lower()
                values = [get(x) for x in a[3:]]
                if target == "utility.getcurrentgametime":
                    result = self.day
                elif target == "game.getplayer":
                    result = self.player
                elif target == "debug.trace":
                    self.traces.append(values[0])
                    result = None
                elif target == "game.querystat":
                    result = self.stats[values[0]]
                elif target == "game.getformfromfile":
                    result = self.plugins.get((values[1], values[0]))
                elif target == "utility.wait":
                    result = None
                elif target == "debug.notification":
                    self.notifications.append(values[0])
                    result = None
                else:
                    raise RuntimeError("Unsupported static native: " + target)
                put(a[2], result)
            elif op == "PROPGET":
                put(a[2], get(a[1]).vars["::" + a[0].lower() + "_var"])
            elif op == "PROPSET":
                get(a[1]).vars["::" + a[0].lower() + "_var"] = get(a[2])
            elif op in ("IADD", "FADD", "ISUBTRACT", "FSUBTRACT", "FMULTIPLY", "STRCAT", "COMPAREEQ", "COMPARELT", "COMPARELTE", "COMPAREGT", "COMPAREGTE"):
                x, y = get(a[1]), get(a[2])
                if op in ("IADD", "FADD", "STRCAT"):
                    result = x + y
                elif op in ("ISUBTRACT", "FSUBTRACT"):
                    result = x - y
                elif op == "FMULTIPLY":
                    result = x * y
                elif op == "COMPAREEQ":
                    result = x == y
                elif op == "COMPARELT":
                    result = x < y
                elif op == "COMPARELTE":
                    result = x <= y
                elif op == "COMPAREGT":
                    result = x > y
                else:
                    result = x >= y
                put(a[0], result)
            else:
                raise RuntimeError("Unsupported opcode: " + op)


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = json.loads((ROOT / "content/campaign.json").read_text())
KINDS = {"nights": 1, "residenceDays": 2, "visited": 3, "deliver": 4, "holds": 5, "stageDone": 6, "questBegun": 7,
         "questNotBegun": 8, "playerInFaction": 9, "actorInFaction": 10, "actorHolds": 11, "actorDead": 12, "actorAlive": 13,
         "globalAtLeast": 14, "earned": 15, "level": 16, "magic": 17, "daysInPhase": 18, "phaseWeight": 19, "present": 20,
         "questCompleted": 21, "stageAtLeast": 22}
# Accounts runs against the original prototype numbers; the plugin binds the campaign's own.
OPERATION = 1002


class World:
    """Test doubles for the vanilla forms the campaign reads, keyed by the IDs in campaign.json."""

    def __init__(self, vm):
        self.vm = vm
        self.places, self.quests, self.actors, self.globals = {}, {}, {}, {}

    def place(self, form):
        return self.places.setdefault(form, Place(form))

    def quest(self, form):
        return self.quests.setdefault(form, VanillaQuest(form))

    def actor(self, form):
        return self.actors.setdefault(form, Inventory())

    def form(self, kind, form, other=False):
        if form is None:
            return None
        if form == "LIST":
            return self.arcanaeum
        if kind in ("visited",):
            return self.place(form)
        if kind in ("stageDone", "questBegun", "questNotBegun", "questCompleted", "stageAtLeast"):
            return self.quest(form)
        if kind in ("actorInFaction", "actorHolds", "actorDead", "actorAlive") and not other:
            return self.actor(form)
        if kind == "globalAtLeast":
            return self.globals.setdefault(form, Global())
        return form  # items, books and factions are plain names


def wire_service(vm, service):
    """Bind Service exactly as the builder does, from content/campaign.json."""
    world = vm.world = World(vm)
    world.arcanaeum = FormList(list(CAMPAIGN["arcanaeum"]["books"]))
    conditions = []
    def add(conds):
        start = len(conditions)
        conditions.extend(conds)
        return start
    ins = CAMPAIGN["instructions"]
    starts, counts, requires, alts = [], [], [], []
    for i in ins:
        starts.append(add(i["conditions"])); counts.append(len(i["conditions"]))
        requires.append(add([i["require"]]) if "require" in i else -1)
        alts.append(add([i["alt"]]) if "alt" in i else -1)
    letter_starts, letter_counts, enclosures, enc_start, enc_count = [], [], [], [], []
    for letter in CAMPAIGN["letters"]:
        letter_starts.append(add(letter["conditions"])); letter_counts.append(len(letter["conditions"]))
        enc_start.append(len(enclosures) if letter["enclosures"] else -1); enc_count.append(len(letter["enclosures"]))
        enclosures.extend(letter["enclosures"])
    key = lambda doc: doc["editorID"]
    service.prop("Orders", [key(i["order"]) for i in ins]).prop("Reports", [key(i["report"]) for i in ins])
    service.prop("Replies", [key(i["reply"]) for i in ins]).prop("AltReplies", [key(i["altReply"]) if "altReply" in i else None for i in ins])
    service.prop("Phases", [i["phase"] for i in ins]).prop("CondStart", starts).prop("CondCount", counts)
    service.prop("RequireCond", requires).prop("AltCond", alts).prop("Weights", [i["weight"] for i in ins])
    service.prop("AltWeights", [i["altWeight"] for i in ins]).prop("AltTrust", [i["altTrust"] for i in ins])
    service.prop("NotYetMessages", [Menu() for _ in ins])
    service.prop("Letters", [key(l["letter"]) for l in CAMPAIGN["letters"]]).prop("LetterPhases", [l["phase"] for l in CAMPAIGN["letters"]])
    service.prop("LetterCondStart", letter_starts).prop("LetterCondCount", letter_counts).prop("LetterActions", [l["action"] for l in CAMPAIGN["letters"]])
    service.prop("EnclosureStart", enc_start).prop("EnclosureCount", enc_count).prop("Enclosures", enclosures)
    service.prop("WanderLetter", key(CAMPAIGN["wander"]))
    service.prop("CondKinds", [KINDS[c["kind"]] for c in conditions])
    service.prop("CondForms", [world.form(c["kind"], c.get("form")) for c in conditions])
    service.prop("CondOtherForms", [world.form(c["kind"], c.get("other"), other=True) for c in conditions])
    service.prop("CondValues", [c["value"] for c in conditions])
    service.prop("CondPlugins", [c.get("plugin", "") for c in conditions]).prop("CondFormIDs", [c.get("local", 0) for c in conditions])
    service.prop("Inn", world.place(CAMPAIGN["places"]["inn"]))
    service.prop("Bounds", [world.place(b) for b in CAMPAIGN["places"]["bounds"]])
    service.prop("AdvanceOperation", CAMPAIGN["operations"]["advance"]).prop("RemovalOperation", CAMPAIGN["operations"]["removal"])
    service.prop("FailureMessages", [Menu() for _ in CAMPAIGN["messages"]["failure"]]).prop("SummaryMessage", Menu())
    return world


def fixture(directory):
    """Wire the scripts as the plugin does, with the service commissioned and Accounts' operation open."""
    vm = VM(directory)
    core = vm.instance("EA_Core")
    dispatch = vm.instance("EA_Dispatch").prop("Core", core).prop("Archive", Inventory())
    service = vm.instance("EA_Service").prop("Core", core).prop("Dispatch", dispatch)
    accounts = vm.instance("EA_Accounts").prop("Core", core).prop("Dispatch", dispatch)
    wire_service(vm, service)
    accounts.prop("FailureMessages", [Menu() for _ in range(11)])
    for p in ("Gold", "AdvanceReceipt", "ReturnReceipt", "AuditNotice", "ExplanationForm", "PersonalExplanationForm", "MealPartialDecision"):
        accounts.prop(p, p)
    for p in ("ClaimForms", "Decisions"):
        accounts.prop(p, [f"{p}{i}" for i in range(4)])
    accounts.prop("BalanceMessage", Menu())
    accounts.prop("OperationID", OPERATION).prop("AdvanceAmount", 80).prop("ClaimAmounts", [30, 80, 30, 30])
    accounts.prop("AllowedAmount", 30).prop("ExplainedAllowance", 15)
    core.call("Commission")
    dispatch.call("Initialize")
    core.call("RegisterAssignment", OPERATION, 4, 0.0)
    return vm, core, dispatch, service, accounts
