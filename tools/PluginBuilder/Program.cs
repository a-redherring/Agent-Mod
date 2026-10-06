using System.Text.Json;
using Mutagen.Bethesda;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Binary.Parameters;
using Mutagen.Bethesda.Plugins.Records;
using Mutagen.Bethesda.Skyrim;

var root = args.Length > 0 ? Path.GetFullPath(args[0]) : Directory.GetCurrentDirectory();
using var buildConfig = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "content/build-config.json")));
var version = buildConfig.RootElement.GetProperty("version").GetString();
var output = Path.Combine(root, "build", "Data");
Directory.CreateDirectory(output);
var names = new[] { "EA_Core", "EA_Dispatch", "EA_Service", "EA_Accounts", "EA_Prototype", "EA_Start" };
var mods = names.ToDictionary(n => n, n => new SkyrimMod(ModKey.FromNameAndExtension(n + ".esp"), SkyrimRelease.SkyrimSE));
var forms = new Dictionary<string, FormKey>();
FormKey Vanilla(uint id) => new(ModKey.FromNameAndExtension("Skyrim.esm"), id);
FormKey Key(string mod, uint id, string editorID)
{
    var key = new FormKey(mods[mod].ModKey, id);
    if (!forms.TryAdd(editorID, key)) throw new InvalidDataException("Duplicate EditorID: " + editorID);
    return key;
}
foreach (var mod in mods.Values)
{
    // No extended FormID range is used; retain compatibility with older SE runtimes.
    mod.ModHeader.Stats.Version = 1.70f;
    mod.ModHeader.Author = "Elenwen Agent Project";
    mod.ModHeader.Description = version + ". New-save testing only; see README. No vanilla quest overrides.";
}
Quest MakeQuest(string mod, uint id, string editorID, string name)
{
    var quest = new Quest(Key(mod, id, editorID), SkyrimRelease.SkyrimSE)
    {
        EditorID = editorID, Name = name, Priority = 30, Flags = 0,
        Type = Quest.TypeEnum.SideQuest, NextAliasID = 0,
        VirtualMachineAdapter = new QuestAdapter { Version = 5, ObjectFormat = 2 }
    };
    mods[mod].Quests.Add(quest);
    return quest;
}
var core = MakeQuest("EA_Core", 0x800, "EA_CoreQuest", "Confidential Service");
var dispatch = MakeQuest("EA_Dispatch", 0x800, "EA_DispatchQuest", "Embassy Correspondence");
var service = MakeQuest("EA_Service", 0x800, "EA_ServiceQuest", "Field Instructions");
var accounts = MakeQuest("EA_Accounts", 0x800, "EA_AccountsQuest", "Operational Accounts");
var prototype = MakeQuest("EA_Prototype", 0x801, "EA_PrototypeQuest", "Confidential Commission");
var startData = JsonSerializer.Deserialize<StartContent>(File.ReadAllText(Path.Combine(root, "content", "start.json")), new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;
var start = MakeQuest("EA_Start", Convert.ToUInt32(startData.Quest.Id, 16), startData.Quest.EditorID, startData.Quest.Name);
var json = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
var docs = JsonSerializer.Deserialize<List<Document>>(File.ReadAllText(Path.Combine(root, "content", "documents.json")), json)!;
var campaign = JsonSerializer.Deserialize<Campaign>(File.ReadAllText(Path.Combine(root, "content", "campaign.json")), json)!;
if (campaign.Instructions.Count == 0 || campaign.Instructions.Count > 32) throw new InvalidDataException("Service supports one to thirty-two instructions");
if (campaign.Letters.Count > 64) throw new InvalidDataException("Service supports up to sixty-four letters");
for (var i = 0; i < campaign.Instructions.Count; i++)
{
    // Instruction index is the assignment offset; the script derives one from the other.
    if (campaign.Instructions[i].Assignment != 2001 + i) throw new InvalidDataException("Instructions must be numbered from 2001 without gaps");
    if ((campaign.Instructions[i].AltReply == null) != (campaign.Instructions[i].Alt == null)) throw new InvalidDataException("An alternative reply needs its condition, and the reverse");
}
Book MakeBook(string module, Document doc)
{
    var book = new Book(Key(module, Convert.ToUInt32(doc.Id, 16), doc.EditorID), SkyrimRelease.SkyrimSE)
    {
        EditorID = doc.EditorID, Name = doc.Title, Type = Book.BookType.NoteOrScroll,
        Model = new Model { File = @"Clutter\Books\Note01.nif" },
        InventoryArt = new FormLinkNullable<IStaticGetter>(Vanilla(0x97788)),
        BookText = "<font face='$HandwrittenFont'><p align='left'>" + System.Net.WebUtility.HtmlEncode(doc.Text).Replace("\n", "<br>") + "</p></font>",
        Value = 0, Weight = 0
    };
    mods[module].Books.Add(book);
    return book;
}
foreach (var doc in docs) MakeBook(doc.Module, doc);
foreach (var doc in startData.Documents) MakeBook("EA_Start", doc);
foreach (var instruction in campaign.Instructions)
{
    MakeBook("EA_Service", instruction.Order);
    MakeBook("EA_Service", instruction.Report);
    MakeBook("EA_Service", instruction.Reply);
    if (instruction.AltReply != null) MakeBook("EA_Service", instruction.AltReply);
}
foreach (var letter in campaign.Letters) MakeBook("EA_Service", letter.Letter);
MakeBook("EA_Service", campaign.Wander);
var arcanaeum = new FormList(Key("EA_Service", Convert.ToUInt32(campaign.Arcanaeum.Id, 16), campaign.Arcanaeum.EditorID), SkyrimRelease.SkyrimSE) { EditorID = campaign.Arcanaeum.EditorID };
foreach (var book in campaign.Arcanaeum.Books) arcanaeum.Items.Add(new FormLink<ISkyrimMajorRecordGetter>(Vanilla(Convert.ToUInt32(book, 16))));
mods["EA_Service"].FormLists.Add(arcanaeum);
var archive = new Container(Key("EA_Dispatch", 0x801, "EA_DocumentArchive"), SkyrimRelease.SkyrimSE)
{
    EditorID = "EA_DocumentArchive", Name = "Filed Correspondence", Flags = 0,
    Model = new Model { File = @"Clutter\Common\StrongBox01.nif" }
};
mods["EA_Dispatch"].Containers.Add(archive);
var box = new Mutagen.Bethesda.Skyrim.Activator(Key("EA_Prototype", 0x800, "EA_SecureDispatch"), SkyrimRelease.SkyrimSE)
{
    EditorID = "EA_SecureDispatch", Name = "Secure Dispatch Box", ActivateTextOverride = "Use",
    Model = new Model { File = @"Clutter\Common\StrongBox01.nif" },
    VirtualMachineAdapter = new VirtualMachineAdapter { Version = 5, ObjectFormat = 2 }
};
mods["EA_Prototype"].Activators.Add(box);
var caseItem = new MiscItem(Key("EA_Prototype", Convert.ToUInt32(startData.Prototype.Case.Id, 16), startData.Prototype.Case.EditorID), SkyrimRelease.SkyrimSE)
{
    EditorID = startData.Prototype.Case.EditorID, Name = startData.Prototype.Case.Name,
    Model = new Model { File = @"Clutter\Common\StrongBox01.nif" }, Value = 0, Weight = 2,
    VirtualMachineAdapter = new VirtualMachineAdapter { Version = 5, ObjectFormat = 2 }
};
mods["EA_Prototype"].MiscItems.Add(caseItem);
Message MakeMessage(string module, uint id, string editorID, string text, params string[] buttons)
{
    var message = new Message(Key(module, id, editorID), SkyrimRelease.SkyrimSE)
    {
        EditorID = editorID, Description = text, Flags = Message.Flag.MessageBox
    };
    foreach (var button in buttons) message.MenuButtons.Add(new MessageButton { Text = button });
    mods[module].Messages.Add(message);
    return message;
}
MakeMessage("EA_Prototype", 0x810, "EA_CommissionMenu", "A sealed packet bears the agreed mark. Break the seal and resume your confidential duties?", "Open commission", "Leave");
MakeMessage("EA_Prototype", 0x811, "EA_MainMenu", "The dispatch case. Reports are answered a day after filing. Copies of everything are kept in the case.", "File Report", "Check Correspondence", "Accounts", "Review status", "Case and archive", "Leave");
MakeMessage("EA_Prototype", 0x812, "EA_AssignmentMenu", "Which instruction does your report answer? Open instructions, in the order they were given; the number is on each order.\n\n1: %.0f   2: %.0f   3: %.0f   4: %.0f\n5: %.0f   6: %.0f   7: %.0f   8: %.0f\n\nA position showing 0 is empty.", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Cancel");
MakeMessage("EA_Prototype", 0x813, "EA_AccountsMenu", "Accounts: the authorised advance and its claim. Only one advance and one claim may be entered.", "Collect authorised advance", "Submit claim / explanation", "Return outstanding funds", "Read statement", "Cancel");
MakeMessage("EA_Prototype", 0x814, "EA_ClaimMenu", "Declare the expense you actually incurred. A personal cost must not be represented as an operational one.", "Fee: 500 septims", "Fee and expenses: 650 septims", "A gift: 60 septims", "A meal: 40 septims", "Cancel");
MakeMessage("EA_Prototype", 0x815, "EA_ExplanationMenu", "Accounts requires an explanation of the meal. Select the accurate statement.", "A necessary meeting", "A personal expense", "Cancel");
MakeMessage("EA_Prototype", 0x816, "EA_FiledMessage", "Filed. A reply, where one is due, will be in the case after a full day.", "Close");
MakeMessage("EA_Prototype", 0x817, "EA_UnavailableMessage", "The case could not be opened. Leave it and try again. If the problem persists, consult the test profile's Papyrus log.", "Close");
MakeMessage("EA_Prototype", 0x818, "EA_CollectedMessage", "Correspondence collected: %.0f. Copies remain in the case.", "Close");
MakeMessage("EA_Accounts", 0x820, "EA_BalanceMessage", "Outstanding advance: %.0f septims\nOwed to Accounts: %.0f septims\nExpenses allowed: %.0f septims\nReimbursed: %.0f septims", "Close");
MakeMessage("EA_Prototype", 0x819, "EA_RepaymentMenu", "Choose how much to return. The payment is limited to the balance outstanding and the gold you carry.", "Up to 10 septims", "Up to 25 septims", "All I can repay", "Cancel");
MakeMessage("EA_Prototype", 0x81A, "EA_ReturnedMessage", "Returned: %.0f septims\nStill outstanding: %.0f septims\n\nThe receipt is in the case.", "Close");
foreach (var m in campaign.Messages.Failure) MakeMessage("EA_Service", Convert.ToUInt32(m.Id, 16), m.EditorID, m.Text, "Close");
MakeMessage("EA_Service", Convert.ToUInt32(campaign.Messages.Summary.Id, 16), campaign.Messages.Summary.EditorID, campaign.Messages.Summary.Text, "Close");
foreach (var instruction in campaign.Instructions) MakeMessage("EA_Service", Convert.ToUInt32(instruction.NotYet.Id, 16), instruction.NotYet.EditorID, instruction.NotYet.Text, "Close");
foreach (var m in startData.Prototype.Messages) MakeMessage("EA_Prototype", Convert.ToUInt32(m.Id, 16), m.EditorID, m.Text, m.Buttons);
foreach (var m in startData.Messages) MakeMessage("EA_Start", Convert.ToUInt32(m.Id, 16), m.EditorID, m.Text, m.Buttons);
MakeMessage("EA_Accounts", 0x900, "EA_AccountsFailure0", "The advance has already been issued. It cannot be collected again. The statement shows what remains.", "Close");
MakeMessage("EA_Accounts", 0x901, "EA_AccountsFailure1", "Accounts has suspended further advances. Settle the liability shown on your statement.", "Close");
MakeMessage("EA_Accounts", 0x902, "EA_AccountsFailure2", "The instruction this advance is for is not open. An advance cannot be drawn once its report is filed.", "Close");
MakeMessage("EA_Accounts", 0x903, "EA_AccountsFailure3", "No advance has been authorised.", "Close");
MakeMessage("EA_Accounts", 0x904, "EA_AccountsFailure4", "File the report on the hire before claiming its cost. This claim covers nothing else.", "Close");
MakeMessage("EA_Accounts", 0x905, "EA_AccountsFailure5", "Your claim or explanation is already awaiting a reply. Check the case after a full day.", "Close");
MakeMessage("EA_Accounts", 0x906, "EA_AccountsFailure6", "The claim is already settled. A second claim cannot be entered.", "Close");
MakeMessage("EA_Accounts", 0x907, "EA_AccountsFailure7", "No new claim can be accepted now. If the meal was returned, choose Submit claim / explanation and explain it.", "Close");
MakeMessage("EA_Accounts", 0x908, "EA_AccountsFailure8", "There is no outstanding advance or debt to repay.", "Close");
MakeMessage("EA_Accounts", 0x909, "EA_AccountsFailure9", "You have no septims to return. The balance remains on the statement.", "Close");
MakeMessage("EA_Accounts", 0x90A, "EA_AccountsFailure10", "Accounts cannot enter this. Nothing has been transferred. Check the case and its archive before trying again.", "Close");
for (var i = 0; i < campaign.Instructions.Count; i++)
{
    service.Objectives.Add(new QuestObjective { Index = (ushort)(100 + i), DisplayText = campaign.Instructions[i].Objective });
    service.Objectives.Add(new QuestObjective { Index = (ushort)(200 + i), DisplayText = "Collect the reply to instruction " + campaign.Instructions[i].Assignment });
}
ScriptObjectProperty Link(string name, FormKey target) => new()
{
    Name = name, Flags = ScriptProperty.Flag.Edited,
    Object = new FormLink<ISkyrimMajorRecordGetter>(target), Alias = -1
};
ScriptObjectListProperty Links(string name, params string[] targets)
{
    var property = new ScriptObjectListProperty { Name = name, Flags = ScriptProperty.Flag.Edited };
    foreach (var target in targets) property.Objects.Add(Link("", target == "" ? FormKey.Null : forms[target]));
    return property;
}
ScriptIntProperty Int(string name, int value) => new() { Name = name, Flags = ScriptProperty.Flag.Edited, Data = value };
ScriptIntListProperty Ints(string name, IEnumerable<int> values)
{
    var property = new ScriptIntListProperty { Name = name, Flags = ScriptProperty.Flag.Edited };
    property.Data.AddRange(values);
    return property;
}
ScriptStringListProperty Strings(string name, IEnumerable<string> values)
{
    var property = new ScriptStringListProperty { Name = name, Flags = ScriptProperty.Flag.Edited };
    property.Data.AddRange(values);
    return property;
}
ScriptObjectListProperty FormLinks(string name, IEnumerable<FormKey> targets)
{
    var property = new ScriptObjectListProperty { Name = name, Flags = ScriptProperty.Flag.Edited };
    foreach (var target in targets) property.Objects.Add(Link("", target));
    return property;
}
ScriptObjectListProperty VanillaLinks(string name, IEnumerable<uint> targets) => FormLinks(name, targets.Select(Vanilla));
ScriptEntry Script(string name, params ScriptProperty[] properties)
{
    var entry = new ScriptEntry { Name = name, Flags = ScriptEntry.Flag.Local };
    entry.Properties.AddRange(properties);
    return entry;
}
ScriptObjectProperty Ref(string property, string editorID) => Link(property, forms[editorID]);
core.VirtualMachineAdapter!.Scripts.Add(Script("EA_Core"));
dispatch.VirtualMachineAdapter!.Scripts.Add(Script("EA_Dispatch", Ref("Core", "EA_CoreQuest")));
// Conditions are one flat table; instructions and letters own consecutive ranges of it.
var kinds = new Dictionary<string, int>
{
    ["nights"] = 1, ["residenceDays"] = 2, ["visited"] = 3, ["deliver"] = 4, ["holds"] = 5, ["stageDone"] = 6,
    ["questBegun"] = 7, ["questNotBegun"] = 8, ["playerInFaction"] = 9, ["actorInFaction"] = 10, ["actorHolds"] = 11,
    ["actorDead"] = 12, ["actorAlive"] = 13, ["globalAtLeast"] = 14, ["earned"] = 15, ["level"] = 16, ["magic"] = 17,
    ["daysInPhase"] = 18, ["phaseWeight"] = 19, ["present"] = 20, ["questCompleted"] = 21, ["stageAtLeast"] = 22
};
var conditions = new List<Condition>();
int AddConditions(IEnumerable<Condition> list) { var first = conditions.Count; conditions.AddRange(list); return first; }
FormKey ConditionForm(string? form) => form == null ? FormKey.Null : form == "LIST" ? arcanaeum.FormKey : Vanilla(Convert.ToUInt32(form, 16));
var condStart = new List<int>(); var condCount = new List<int>(); var requireCond = new List<int>(); var altCond = new List<int>();
foreach (var instruction in campaign.Instructions)
{
    condStart.Add(AddConditions(instruction.Conditions)); condCount.Add(instruction.Conditions.Count);
    requireCond.Add(instruction.Require == null ? -1 : AddConditions(new[] { instruction.Require }));
    altCond.Add(instruction.Alt == null ? -1 : AddConditions(new[] { instruction.Alt }));
}
var letterStart = new List<int>(); var letterCount = new List<int>();
var enclosures = new List<string>(); var enclosureStart = new List<int>(); var enclosureCount = new List<int>();
foreach (var letter in campaign.Letters)
{
    letterStart.Add(AddConditions(letter.Conditions)); letterCount.Add(letter.Conditions.Count);
    enclosureStart.Add(letter.Enclosures.Count == 0 ? -1 : enclosures.Count); enclosureCount.Add(letter.Enclosures.Count);
    enclosures.AddRange(letter.Enclosures);
}
if (conditions.Count > 128) throw new InvalidDataException("Service supports up to 128 conditions");
foreach (var c in conditions) if (!kinds.ContainsKey(c.Kind)) throw new InvalidDataException("Unknown condition kind: " + c.Kind);
var instructions = campaign.Instructions;
service.VirtualMachineAdapter!.Scripts.Add(Script("EA_Service",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"),
    Links("Orders", instructions.Select(i => i.Order.EditorID).ToArray()), Links("Reports", instructions.Select(i => i.Report.EditorID).ToArray()),
    Links("Replies", instructions.Select(i => i.Reply.EditorID).ToArray()), Links("AltReplies", instructions.Select(i => i.AltReply?.EditorID ?? "").ToArray()),
    Ints("Phases", instructions.Select(i => i.Phase)), Ints("CondStart", condStart), Ints("CondCount", condCount),
    Ints("RequireCond", requireCond), Ints("AltCond", altCond), Ints("Weights", instructions.Select(i => i.Weight)),
    Ints("AltWeights", instructions.Select(i => i.AltWeight)), Ints("AltTrust", instructions.Select(i => i.AltTrust)),
    Links("NotYetMessages", instructions.Select(i => i.NotYet.EditorID).ToArray()),
    Links("Letters", campaign.Letters.Select(l => l.Letter.EditorID).ToArray()), Ints("LetterPhases", campaign.Letters.Select(l => l.Phase)),
    Ints("LetterCondStart", letterStart), Ints("LetterCondCount", letterCount), Ints("LetterActions", campaign.Letters.Select(l => l.Action)),
    Ints("EnclosureStart", enclosureStart), Ints("EnclosureCount", enclosureCount), VanillaLinks("Enclosures", enclosures.Select(e => Convert.ToUInt32(e, 16))),
    Ref("WanderLetter", campaign.Wander.EditorID),
    Ints("CondKinds", conditions.Select(c => kinds[c.Kind])), FormLinks("CondForms", conditions.Select(c => ConditionForm(c.Form))),
    FormLinks("CondOtherForms", conditions.Select(c => ConditionForm(c.Other))), Ints("CondValues", conditions.Select(c => c.Value)),
    Strings("CondPlugins", conditions.Select(c => c.Plugin ?? "")), Ints("CondFormIDs", conditions.Select(c => c.Local ?? 0)),
    Link("Inn", Vanilla(Convert.ToUInt32(campaign.Places.Inn, 16))), VanillaLinks("Bounds", campaign.Places.Bounds.Select(b => Convert.ToUInt32(b, 16))),
    Int("AdvanceOperation", campaign.Operations.Advance), Int("RemovalOperation", campaign.Operations.Removal),
    Links("FailureMessages", campaign.Messages.Failure.Select(m => m.EditorID).ToArray()), Ref("SummaryMessage", campaign.Messages.Summary.EditorID)));
accounts.VirtualMachineAdapter!.Scripts.Add(Script("EA_Accounts",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"), Link("Gold", Vanilla(0xF)),
    Ref("AdvanceReceipt", "EA_AdvanceReceipt"), Ref("ReturnReceipt", "EA_ReturnReceipt"), Ref("AuditNotice", "EA_AuditNotice"),
    Links("ClaimForms", "EA_ClaimSupplies", "EA_ClaimExtravagant", "EA_ClaimGift", "EA_ClaimMeal"),
    Links("Decisions", "EA_ClaimApproved", "EA_ClaimPartial", "EA_ClaimDenied", "EA_ClaimReturned"),
    Ref("ExplanationForm", "EA_ExplanationForm"), Ref("PersonalExplanationForm", "EA_ExplanationPersonal"),
    Links("FailureMessages", Enumerable.Range(0, 11).Select(i => "EA_AccountsFailure" + i).ToArray()),
    Ref("MealPartialDecision", "EA_MealPartialDecision"), Ref("BalanceMessage", "EA_BalanceMessage"),
    // The hire of the Dunmer: a 500-septim advance; claims of 500, 650, 60 and 40.
    Int("OperationID", campaign.Operations.Advance), Int("AdvanceAmount", 500), Ints("ClaimAmounts", new[] { 500, 650, 60, 40 }),
    Int("AllowedAmount", 500), Int("ExplainedAllowance", 20)));
prototype.VirtualMachineAdapter!.Scripts.Add(Script("EA_Prototype",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"), Ref("Service", "EA_ServiceQuest"),
    Ref("Accounts", "EA_AccountsQuest"), Link("Gold", Vanilla(0xF)), Ref("Commission", "EA_Commission"),
    Ref("ArchiveBase", "EA_DocumentArchive"),
    Ref("CommissionMenu", "EA_CommissionMenu"), Ref("MainMenu", "EA_MainMenu"), Ref("AssignmentMenu", "EA_AssignmentMenu"),
    Ref("AccountsMenu", "EA_AccountsMenu"), Ref("ClaimMenu", "EA_ClaimMenu"), Ref("ExplanationMenu", "EA_ExplanationMenu"),
    Ref("RepaymentMenu", "EA_RepaymentMenu"), Ref("ReturnedMessage", "EA_ReturnedMessage"),
    Ref("FiledMessage", "EA_FiledMessage"), Ref("UnavailableMessage", "EA_UnavailableMessage"), Ref("CollectedMessage", "EA_CollectedMessage"),
    Ref("BoxBase", "EA_SecureDispatch"), Ref("CaseItem", startData.Prototype.Case.EditorID), Ref("CaseMenu", "EA_CaseMenu")));
caseItem.VirtualMachineAdapter!.Scripts.Add(Script("EA_DispatchCase", Ref("Controller", "EA_PrototypeQuest")));
// Alternate Perspective starts this quest; stage 10 is its start-up stage and moves the player at once.
foreach (var stage in startData.Quest.Stages)
{
    var entry = new QuestLogEntry { Entry = stage.Log, Flags = 0 };
    if (stage.Complete) entry.Flags = QuestLogEntry.Flag.CompleteQuest;
    start.Stages.Add(new QuestStage { Index = (ushort)stage.Index, Flags = stage.StartUp ? QuestStage.Flag.StartUpStage : 0, LogEntries = { entry } });
}
foreach (var objective in startData.Quest.Objectives)
    start.Objectives.Add(new QuestObjective { Index = (ushort)objective.Index, DisplayText = objective.Text });
start.Aliases.Add(new QuestAlias { ID = 0, Type = QuestAlias.TypeEnum.Location, Name = "Northwatch", SpecificLocation = new FormLinkNullable<ILocationGetter>(Vanilla(0x19285)) });
start.Aliases.Add(new QuestAlias { ID = 1, Name = "Arrival", Location = new LocationAliasReference { AliasID = 0, RefType = new FormLinkNullable<ILocationReferenceTypeGetter>(Vanilla(0x10F63C)) } });
start.Aliases.Add(new QuestAlias { ID = 2, Name = "Player", ForcedReference = new FormLinkNullable<IPlacedGetter>(Vanilla(0x14)) });
start.NextAliasID = 3;
var startScript = (QuestAdapter)start.VirtualMachineAdapter!;
startScript.Scripts.Add(Script("EA_Opening",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"), Ref("Service", "EA_ServiceQuest"),
    Link("NorthwatchFaction", Vanilla(0xC0637)), Ref("SealedPacket", "EA_SealedPacket"),
    Links("PacketPapers", "EA_ArrivalLetter", "EA_CivilianPapers", "EA_ConditionalRelease", "EA_DispatchInstructions"),
    VanillaLinks("PacketBooks", campaign.PacketBooks.Select(b => Convert.ToUInt32(b, 16))),
    Ref("DispatchCase", startData.Prototype.Case.EditorID), Link("Gold", Vanilla(0xF)), Link("Dagger", Vanilla(0x1397E)),
    Int("Allowance", 100)));
startScript.FileName = "EA_Opening";
startScript.ExtraBindDataVersion = 2;
startScript.Fragments.Add(new QuestScriptFragment { Stage = 10, StageIndex = 0, Unknown2 = 1, ScriptName = "EA_Opening", FragmentName = "Fragment_10" });
var packetBook = mods["EA_Start"].Books.First(b => b.EditorID == "EA_SealedPacket");
packetBook.VirtualMachineAdapter = new VirtualMachineAdapter { Version = 5, ObjectFormat = 2 };
packetBook.VirtualMachineAdapter.Scripts.Add(Script("EA_SealedPacket", Ref("Opening", startData.Quest.EditorID)));
var registration = Path.Combine(output, "SKSE", "AlternatePerspective");
Directory.CreateDirectory(registration);
File.WriteAllText(Path.Combine(registration, "ElenwenAgent.json"), JsonSerializer.Serialize(startData.AlternatePerspective, new JsonSerializerOptions { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }) + "\n");
box.VirtualMachineAdapter!.Scripts.Add(Script("EA_DispatchBox", Ref("Controller", "EA_PrototypeQuest")));
// The player alias reports arrivals and nights; Service decides what they count for.
service.Aliases.Add(new QuestAlias { ID = 0, Name = "Player", ForcedReference = new FormLinkNullable<IPlacedGetter>(Vanilla(0x14)) });
service.NextAliasID = 1;
((QuestAdapter)service.VirtualMachineAdapter!).Aliases.Add(new QuestFragmentAlias
{
    Property = new ScriptObjectProperty { Object = new FormLink<ISkyrimMajorRecordGetter>(service.FormKey), Alias = 0 },
    Version = 5, ObjectFormat = 2, Scripts = { Script("EA_ServicePlayer", Ref("Service", "EA_ServiceQuest")) }
});
// Explicit IDs form the save contract. Fail instead of silently allocating new IDs.
var recordMap = new SortedDictionary<string, string>();
foreach (var (name, mod) in mods)
{
    foreach (var record in mod.EnumerateMajorRecords())
    {
        if (record.FormKey.ModKey != mod.ModKey) throw new InvalidDataException("Unexpected override");
        recordMap.Add(record.EditorID!, record.FormKey.ToString());
    }
    mod.ModHeader.Stats.NextFormID = mod.EnumerateMajorRecords().Max(r => r.FormKey.ID) + 1;
    var path = Path.Combine(output, name + ".esp");
    var loadOrder = names.Select(n => mods[n].ModKey).Prepend(ModKey.FromNameAndExtension("Skyrim.esm"));
    mod.WriteToBinary(path, new BinaryWriteParameters { MastersListOrdering = new MastersListOrderingByLoadOrder(loadOrder) });
    using var read = SkyrimMod.CreateFromBinaryOverlay(path, SkyrimRelease.SkyrimSE);
    if (read.EnumerateMajorRecords().Count() != mod.EnumerateMajorRecords().Count()) throw new InvalidDataException("Record round trip failed");
    Console.WriteLine($"{name}.esp: {read.EnumerateMajorRecords().Count()} records; masters: {string.Join(", ", read.ModHeader.MasterReferences.Select(m => m.Master))}");
}
File.WriteAllText(Path.Combine(root, "build", "record-map.json"), JsonSerializer.Serialize(recordMap, new JsonSerializerOptions { WriteIndented = true }) + "\n");
record Document(string Module, string Id, string EditorID, string Title, string Text);
record MessageText(string Id, string EditorID, string Text, string[] Buttons);
record Condition(string Kind, string? Form, string? Other, int Value, string? Plugin, int? Local);
record Instruction(int Assignment, string Key, int Phase, string Objective, Document Order, Document Report, Document Reply, Document? AltReply,
    MessageText NotYet, List<Condition> Conditions, Condition? Require, Condition? Alt, int Weight, int AltWeight, int AltTrust);
record LetterSpec(string Key, int Phase, int Action, Document Letter, List<Condition> Conditions, List<string> Enclosures);
record Arcanaeum(string Id, string EditorID, List<string> Books);
record Places(string Inn, List<string> Bounds);
record Operations(int Advance, int Removal);
record CampaignMessages(List<MessageText> Failure, MessageText Summary);
record Campaign(List<Instruction> Instructions, List<LetterSpec> Letters, Document Wander, Arcanaeum Arcanaeum, Places Places, Operations Operations,
    List<string> PacketBooks, CampaignMessages Messages);
record StartStage(int Index, bool StartUp, bool Complete, string Log);
record StartObjective(int Index, string Text);
record StartQuest(string Id, string EditorID, string Name, List<StartStage> Stages, List<StartObjective> Objectives);
record StartItem(string Id, string EditorID, string Name);
record StartPrototype(StartItem Case, List<MessageText> Messages);
record StartContent(StartQuest Quest, List<Document> Documents, List<MessageText> Messages, StartPrototype Prototype, JsonElement AlternatePerspective);
