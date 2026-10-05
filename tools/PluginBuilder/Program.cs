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
var names = new[] { "EA_Core", "EA_Dispatch", "EA_Service", "EA_Accounts", "EA_Prototype" };
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
var docs = JsonSerializer.Deserialize<List<Document>>(File.ReadAllText(Path.Combine(root, "content", "documents.json")), new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;
foreach (var doc in docs)
{
    var book = new Book(Key(doc.Module, Convert.ToUInt32(doc.Id, 16), doc.EditorID), SkyrimRelease.SkyrimSE)
    {
        EditorID = doc.EditorID, Name = doc.Title, Type = Book.BookType.NoteOrScroll,
        Model = new Model { File = @"Clutter\Books\Note01.nif" },
        InventoryArt = new FormLinkNullable<IStaticGetter>(Vanilla(0x97788)),
        BookText = "<font face='$HandwrittenFont'><p align='left'>" + System.Net.WebUtility.HtmlEncode(doc.Text).Replace("\n", "<br>") + "</p></font>",
        Value = 0, Weight = 0
    };
    mods[doc.Module].Books.Add(book);
}
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
MakeMessage("EA_Prototype", 0x810, "EA_CommissionMenu", "A sealed packet bears the mark agreed with Elenwen. Break the seal and resume your confidential duties?", "Open commission", "Leave");
MakeMessage("EA_Prototype", 0x811, "EA_MainMenu", "Secure Embassy dispatch. Replies require one full day in transit. Recoverable copies of your orders are kept on file.", "Collect Orders", "File Report", "Request Extension", "Request Supply Authority", "Accounts", "Check Responses", "Recover filed copies", "Review status", "Leave");
MakeMessage("EA_Prototype", 0x812, "EA_AssignmentMenu", "Select the instruction to which your paper refers.", "Read field protocol", "Deliver three Alto wines", "Deliver six blue flowers", "Deliver six firewood", "Deliver four leather strips", "Deliver six wheat", "Cancel");
MakeMessage("EA_Prototype", 0x813, "EA_AccountsMenu", "Operational accounts: wine procurement, instruction 1002. Only one advance and one claim may be entered for this instruction.", "Collect authorized advance", "Submit claim / explanation", "Return outstanding funds", "Read statement", "Cancel");
MakeMessage("EA_Prototype", 0x814, "EA_ClaimMenu", "Declare the expense you actually incurred. The form will be filed against the wine delivery. A personal cost must not be represented as an Embassy purchase.", "Supplies: 30 septims", "Supplies: 80 septims", "Personal gift: 30 septims", "Meal: 30 septims", "Cancel");
MakeMessage("EA_Prototype", 0x815, "EA_ExplanationMenu", "Accounts requires an explanation of the meal. Select the accurate statement.", "Necessary supplier meeting", "Personal entertainment", "Cancel");
MakeMessage("EA_Prototype", 0x816, "EA_FiledMessage", "The transaction has been entered. Correspondence, where required, will return after the next dispatch run.", "Close");
MakeMessage("EA_Prototype", 0x817, "EA_UnavailableMessage", "The dispatch office could not be opened. Leave the box and try again. If the problem persists, consult the test profile Papyrus log.", "Close");
MakeMessage("EA_Prototype", 0x818, "EA_CollectedMessage", "Responses collected: %.0f. Filed copies remain in the archive.", "Close");
MakeMessage("EA_Accounts", 0x820, "EA_BalanceMessage", "Outstanding advance: %.0f septims\nAmount due to Accounts: %.0f septims\nExpenses allowed: %.0f septims\nCash reimbursed: %.0f septims", "Close");
MakeMessage("EA_Prototype", 0x819, "EA_RepaymentMenu", "Choose how much to return. The payment is limited to the balance outstanding and the gold you carry.", "Up to 10 septims", "Up to 25 septims", "All I can repay", "Cancel");
MakeMessage("EA_Prototype", 0x81A, "EA_ReturnedMessage", "Returned: %.0f septims\nStill outstanding: %.0f septims\n\nYour receipt is filed with Accounts.", "Close");
MakeMessage("EA_Prototype", 0x81B, "EA_ReviewPendingMessage", "The six duties are complete. The closing review awaits your Accounts decision or meal explanation. Resolve the claim through Accounts and collect its response.", "Close");
MakeMessage("EA_Service", 0x900, "EA_ServiceFailure0", "This instruction has not been collected. Choose Collect Orders. Instructions 1004-1006 become available after the first three completion responses have been collected.", "Close");
MakeMessage("EA_Service", 0x901, "EA_ServiceFailure1", "The report has already been filed or the instruction is closed. Check Responses for any outstanding acknowledgment.", "Close");
MakeMessage("EA_Service", 0x902, "EA_ServiceFailure2", "Read the private field papers in your inventory before filing this acknowledgment. Missing papers can be recovered at dispatch.", "Close");
MakeMessage("EA_Service", 0x903, "EA_ServiceFailure3", "An extension request is already awaiting its response. Check Responses after a full day in transit.", "Close");
MakeMessage("EA_Service", 0x904, "EA_ServiceFailure4", "A further extension has already been refused. Complete the work and file the report; overdue work is still accepted.", "Close");
MakeMessage("EA_Service", 0x905, "EA_ServiceFailure5", "Supply authority is already awaiting its response. Collect the authorization before requesting an advance from Accounts.", "Close");
MakeMessage("EA_Service", 0x906, "EA_ServiceFailure6", "Prior supply authority is already held for instruction 1002. Collect the advance under Accounts while the wine duty remains open.", "Close");
MakeMessage("EA_Service", 0x907, "EA_ServiceFailure7", "Dispatch cannot accept another record. No supplies have been taken. Leave the box and try again; if the problem persists, the dispatch or archive requires attention.", "Close");
MakeMessage("EA_Service", 0x910, "EA_MissingSupply0", "Read the private field papers before filing this acknowledgment. Missing papers can be recovered at dispatch.", "Close");
MakeMessage("EA_Service", 0x911, "EA_MissingSupply1", "This consignment is short by %.0f bottles of Alto wine. Bring the required supplies to the dispatch box. Nothing has been taken.", "Close");
MakeMessage("EA_Service", 0x912, "EA_MissingSupply2", "This consignment is short by %.0f blue mountain flowers. Bring the required supplies to the dispatch box. Nothing has been taken.", "Close");
MakeMessage("EA_Service", 0x913, "EA_MissingSupply3", "This consignment is short by %.0f pieces of firewood. Bring the required supplies to the dispatch box. Nothing has been taken.", "Close");
MakeMessage("EA_Service", 0x914, "EA_MissingSupply4", "This consignment is short by %.0f leather strips. Bring the required supplies to the dispatch box. Nothing has been taken.", "Close");
MakeMessage("EA_Service", 0x915, "EA_MissingSupply5", "This consignment is short by %.0f measures of wheat. Bring the required supplies to the dispatch box. Nothing has been taken.", "Close");
MakeMessage("EA_Service", 0x920, "EA_AssignmentStatus0", "Instruction %.0f has not been collected. Choose Collect Orders. The second packet opens after all three responses to the first packet have been collected.", "Close");
MakeMessage("EA_Service", 0x921, "EA_AssignmentStatus1", "Instruction %.0f is active.\nDays remaining: %.1f\n\nFile your report and any required supplies through dispatch.", "Close");
MakeMessage("EA_Service", 0x922, "EA_AssignmentStatus2", "Instruction %.0f is overdue.\nDays past the deadline: %.1f\n\nThe work is still required. File it or request your first extension; an extension applies only when its approval is collected.", "Close");
MakeMessage("EA_Service", 0x923, "EA_AssignmentStatus3", "Instruction %.0f: report filed.\n\nCheck Responses after the full day in transit. The consignment cannot be filed a second time.", "Close");
MakeMessage("EA_Service", 0x924, "EA_AssignmentStatus4", "Instruction %.0f is complete.\n\nThe acknowledgment has been collected. Copies remain in the archive.", "Close");
MakeMessage("EA_Service", 0x930, "EA_StatusSummary", "DISPATCH REGISTER\nActive: %.0f    Overdue: %.0f\nReports filed: %.0f    Completed: %.0f / 6\nReplies ready: %.0f    In transit: %.0f\n\nThe second packet opens after the first three duties are acknowledged. A closing assessment follows all six duties and any pending Accounts decision.", "Inspect instruction", "Close");
MakeMessage("EA_Service", 0x931, "EA_PacketReady", "The first packet is complete. Three further instructions are ready. Choose Collect Orders when you are ready to begin; their deadlines start on collection.", "Close");
MakeMessage("EA_Service", 0x932, "EA_EvaluationQueued", "The closing docket has been filed. Elenwen's assessment will arrive after one full day. Collect it through Check Responses.", "Close");
MakeMessage("EA_Accounts", 0x900, "EA_AccountsFailure0", "The eighty-septim advance has already been issued. It cannot be collected again. Consult the Accounts statement for the remaining balance.", "Close");
MakeMessage("EA_Accounts", 0x901, "EA_AccountsFailure1", "Accounts has suspended further advances. Resolve the outstanding liability shown on your statement.", "Close");
MakeMessage("EA_Accounts", 0x902, "EA_AccountsFailure2", "The wine procurement instruction must be collected and still open before an advance can be issued. An advance cannot be drawn after the delivery report is filed.", "Close");
MakeMessage("EA_Accounts", 0x903, "EA_AccountsFailure3", "Prior supply authority has not been collected. Request Supply Authority at dispatch, allow a full day, then collect the written authorization.", "Close");
MakeMessage("EA_Accounts", 0x904, "EA_AccountsFailure4", "Deliver the three Alto wines and file instruction 1002 before claiming its expense. This claim does not cover the other duties.", "Close");
MakeMessage("EA_Accounts", 0x905, "EA_AccountsFailure5", "Your claim or explanation is already awaiting a response. Check Responses after its full day in transit.", "Close");
MakeMessage("EA_Accounts", 0x906, "EA_AccountsFailure6", "The claim for instruction 1002 is already settled. A second claim cannot be submitted.", "Close");
MakeMessage("EA_Accounts", 0x907, "EA_AccountsFailure7", "No new claim can be accepted at this stage. If the meal claim was returned, choose Submit claim / explanation and provide the requested explanation.", "Close");
MakeMessage("EA_Accounts", 0x908, "EA_AccountsFailure8", "There is no outstanding advance or Accounts debt to repay.", "Close");
MakeMessage("EA_Accounts", 0x909, "EA_AccountsFailure9", "You have no septims available to return. Your outstanding balance remains on the Accounts statement.", "Close");
MakeMessage("EA_Accounts", 0x90A, "EA_AccountsFailure10", "Accounts cannot enter this transaction. No funds have been transferred. Check the dispatch and archive before trying again.", "Close");
for (var i = 0; i < 6; i++)
{
    var objectives = new[] { "Read the field papers, then file an acknowledgment", "Deliver three bottles of Alto wine through dispatch", "Deliver six blue mountain flowers through dispatch", "Deliver six pieces of firewood through dispatch", "Deliver four leather strips through dispatch", "Deliver six measures of wheat through dispatch" };
    service.Objectives.Add(new QuestObjective { Index = (ushort)(10 + i), DisplayText = objectives[i] });
    service.Objectives.Add(new QuestObjective { Index = (ushort)(20 + i), DisplayText = "Collect the response to instruction " + (1001 + i) });
}
service.Objectives.Add(new QuestObjective { Index = 30, DisplayText = "Collect Elenwen's closing assessment" });
ScriptObjectProperty Link(string name, FormKey target) => new()
{
    Name = name, Flags = ScriptProperty.Flag.Edited,
    Object = new FormLink<ISkyrimMajorRecordGetter>(target), Alias = -1
};
ScriptObjectListProperty Links(string name, params string[] targets)
{
    var property = new ScriptObjectListProperty { Name = name, Flags = ScriptProperty.Flag.Edited };
    foreach (var target in targets) property.Objects.Add(Link("", forms[target]));
    return property;
}
ScriptEntry Script(string name, params ScriptProperty[] properties)
{
    var entry = new ScriptEntry { Name = name, Flags = ScriptEntry.Flag.Local };
    entry.Properties.AddRange(properties);
    return entry;
}
ScriptObjectProperty Ref(string property, string editorID) => Link(property, forms[editorID]);
core.VirtualMachineAdapter!.Scripts.Add(Script("EA_Core"));
dispatch.VirtualMachineAdapter!.Scripts.Add(Script("EA_Dispatch", Ref("Core", "EA_CoreQuest")));
service.VirtualMachineAdapter!.Scripts.Add(Script("EA_Service",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"),
    Links("Orders", "EA_OrderProtocol", "EA_OrderWine", "EA_OrderFlowers", "EA_OrderFirewood", "EA_OrderLeather", "EA_OrderWheat"),
    Links("Reports", "EA_ReportProtocol", "EA_ReportWine", "EA_ReportFlowers", "EA_ReportFirewood", "EA_ReportLeather", "EA_ReportWheat"),
    Links("Responses", "EA_ResponseProtocol", "EA_ResponseWine", "EA_ResponseFlowers", "EA_ResponseFirewood", "EA_ResponseLeather", "EA_ResponseWheat"),
    Links("ExtensionRequests", "EA_ExtensionRequest", "EA_ExtensionRequestWine", "EA_ExtensionRequestFlowers", "EA_ExtensionRequestFirewood", "EA_ExtensionRequestLeather", "EA_ExtensionRequestWheat"),
    Links("ApprovedExtensions", "EA_ExtensionApproved", "EA_ExtensionApprovedWine", "EA_ExtensionApprovedFlowers", "EA_ExtensionApprovedFirewood", "EA_ExtensionApprovedLeather", "EA_ExtensionApprovedWheat"),
    Links("DeniedExtensions", "EA_ExtensionDenied", "EA_ExtensionDeniedWine", "EA_ExtensionDeniedFlowers", "EA_ExtensionDeniedFirewood", "EA_ExtensionDeniedLeather", "EA_ExtensionDeniedWheat"),
    Links("PromptResponses", "EA_ResponsePromptProtocol", "EA_ResponsePromptWine", "EA_ResponsePromptFlowers", "EA_ResponsePromptFirewood", "EA_ResponsePromptLeather", "EA_ResponsePromptWheat"),
    Links("LateResponses", "EA_ResponseLateProtocol", "EA_ResponseLateWine", "EA_ResponseLateFlowers", "EA_ResponseLateFirewood", "EA_ResponseLateLeather", "EA_ResponseLateWheat"),
    Links("FailureMessages", "EA_ServiceFailure0", "EA_ServiceFailure1", "EA_ServiceFailure2", "EA_ServiceFailure3", "EA_ServiceFailure4", "EA_ServiceFailure5", "EA_ServiceFailure6", "EA_ServiceFailure7"),
    Links("MissingMessages", "EA_MissingSupply0", "EA_MissingSupply1", "EA_MissingSupply2", "EA_MissingSupply3", "EA_MissingSupply4", "EA_MissingSupply5"),
    Links("StatusMessages", "EA_AssignmentStatus0", "EA_AssignmentStatus1", "EA_AssignmentStatus2", "EA_AssignmentStatus3", "EA_AssignmentStatus4"),
    Ref("SummaryMessage", "EA_StatusSummary"), Ref("PacketReadyMessage", "EA_PacketReady"), Ref("EvaluationQueuedMessage", "EA_EvaluationQueued"),
    Ref("EvaluationRequest", "EA_EvaluationRequest"), Links("Evaluations", "EA_EvaluationGood", "EA_EvaluationMixed", "EA_EvaluationPoor"),
    Ref("AuthorityRequest", "EA_AuthorityRequest"),
    Ref("AuthorityApproved", "EA_AuthorityApproved"), Link("Wine", Vanilla(0x3133B)), Link("Flowers", Vanilla(0x77E1C)),
    Link("Firewood", Vanilla(0x6F993)), Link("LeatherStrips", Vanilla(0x800E4)), Link("Wheat", Vanilla(0x4B0BA))));
accounts.VirtualMachineAdapter!.Scripts.Add(Script("EA_Accounts",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"), Link("Gold", Vanilla(0xF)),
    Ref("AdvanceReceipt", "EA_AdvanceReceipt"), Ref("ReturnReceipt", "EA_ReturnReceipt"), Ref("AuditNotice", "EA_AuditNotice"),
    Links("ClaimForms", "EA_ClaimSupplies", "EA_ClaimExtravagant", "EA_ClaimGift", "EA_ClaimMeal"),
    Links("Decisions", "EA_ClaimApproved", "EA_ClaimPartial", "EA_ClaimDenied", "EA_ClaimReturned"),
    Ref("ExplanationForm", "EA_ExplanationForm"), Ref("PersonalExplanationForm", "EA_ExplanationPersonal"),
    Links("FailureMessages", "EA_AccountsFailure0", "EA_AccountsFailure1", "EA_AccountsFailure2", "EA_AccountsFailure3", "EA_AccountsFailure4", "EA_AccountsFailure5", "EA_AccountsFailure6", "EA_AccountsFailure7", "EA_AccountsFailure8", "EA_AccountsFailure9", "EA_AccountsFailure10"),
    Ref("MealPartialDecision", "EA_MealPartialDecision"), Ref("BalanceMessage", "EA_BalanceMessage")));
prototype.VirtualMachineAdapter!.Scripts.Add(Script("EA_Prototype",
    Ref("Core", "EA_CoreQuest"), Ref("Dispatch", "EA_DispatchQuest"), Ref("Service", "EA_ServiceQuest"),
    Ref("Accounts", "EA_AccountsQuest"), Link("Gold", Vanilla(0xF)), Ref("Commission", "EA_Commission"),
    Ref("FieldPapers", "EA_FieldPapersBook"), Ref("ArchiveBase", "EA_DocumentArchive"),
    Ref("CommissionMenu", "EA_CommissionMenu"), Ref("MainMenu", "EA_MainMenu"), Ref("AssignmentMenu", "EA_AssignmentMenu"),
    Ref("AccountsMenu", "EA_AccountsMenu"), Ref("ClaimMenu", "EA_ClaimMenu"), Ref("ExplanationMenu", "EA_ExplanationMenu"),
    Ref("RepaymentMenu", "EA_RepaymentMenu"), Ref("ReturnedMessage", "EA_ReturnedMessage"), Ref("ReviewPendingMessage", "EA_ReviewPendingMessage"),
    Ref("FiledMessage", "EA_FiledMessage"), Ref("UnavailableMessage", "EA_UnavailableMessage"), Ref("CollectedMessage", "EA_CollectedMessage")));
box.VirtualMachineAdapter!.Scripts.Add(Script("EA_DispatchBox", Ref("Controller", "EA_PrototypeQuest")));
var papers = mods["EA_Core"].Books.First(b => b.EditorID == "EA_FieldPapersBook");
papers.VirtualMachineAdapter = new VirtualMachineAdapter { Version = 5, ObjectFormat = 2 };
papers.VirtualMachineAdapter.Scripts.Add(Script("EA_FieldPapers", Ref("Core", "EA_CoreQuest")));
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
