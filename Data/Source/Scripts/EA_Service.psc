Scriptname EA_Service extends EA_Module
; The campaign. Phases of authored instructions and letters, each gated by conditions read from
; vanilla state; nothing vanilla is ever changed. Instruction i is Core assignment 2001 + i.
; Letter j is dispatch subject 2900 + j; the wander letter is subject 2899.
; Phases: 1 Riverwood residence, 2 released (Markarth), 3 interval, 4 College.

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
Book[] Property Orders Auto
Book[] Property Reports Auto
Book[] Property Replies Auto
; The reply used when AltCond holds at filing; None where an instruction has one reply.
Book[] Property AltReplies Auto
Int[] Property Phases Auto
Int[] Property CondStart Auto
Int[] Property CondCount Auto
; -1, or a condition that must hold before the order is issued at all (an optional plugin).
Int[] Property RequireCond Auto
Int[] Property AltCond Auto
Int[] Property Weights Auto
Int[] Property AltWeights Auto
Int[] Property AltTrust Auto
Message[] Property NotYetMessages Auto
Book[] Property Letters Auto
Int[] Property LetterPhases Auto
Int[] Property LetterCondStart Auto
Int[] Property LetterCondCount Auto
; 0 none, 1 next phase, 2 next phase and advance authority, 3 removal authority.
Int[] Property LetterActions Auto
Int[] Property EnclosureStart Auto
Int[] Property EnclosureCount Auto
Form[] Property Enclosures Auto
Book Property WanderLetter Auto
Int[] Property CondKinds Auto
Form[] Property CondForms Auto
Form[] Property CondOtherForms Auto
Int[] Property CondValues Auto
; A form in a plugin that may be absent is named by file and local ID instead of CondForms.
String[] Property CondPlugins Auto
Int[] Property CondFormIDs Auto
Location Property Inn Auto
Location[] Property Bounds Auto
Int Property AdvanceOperation Auto
Int Property RemovalOperation Auto
Message[] Property FailureMessages Auto
Message Property SummaryMessage Auto
; Condition kinds: 1 nights at the inn, 2 days of residence (plus delay), 3 visited a place,
; 4 deliver an item or one of a list, 5 hold it, 6 quest stage done, 7 quest begun, 8 quest not begun,
; 9 player in faction, 10 actor in faction, 11 actor holds item, 12 actor dead, 13 actor alive,
; 14 global at least, 15 earned own money, 16 level, 17 best magic school, 18 days in phase,
; 19 phase weight, 20 form present, 21 quest completed, 22 quest stage at least.
Int phase = 0
Float phaseStart = 0.0
Int phaseWeight = 0
Float residenceStart = 0.0
Int nights = 0
Float delayDays = 0.0
Bool away = False
Float lastWanderLetter = -100.0
Int baseMostGold = 0
Int lastError = 2
Int notYet = 0
Bool[] issued
Int[] reportTransactions
Bool[] alternative
Bool[] letterSent
Int[] letterTransactions
Bool[] letterDone
Bool[] visited
Bool initialized = False

Function Initialize()
    If initialized
        Return
    EndIf
    issued = new Bool[32]
    reportTransactions = new Int[32]
    alternative = new Bool[32]
    letterSent = new Bool[64]
    letterTransactions = new Int[64]
    letterDone = new Bool[64]
    visited = new Bool[128]
    initialized = True
EndFunction

Function BeginCampaign()
    ; Called once the service is commissioned. Earnings are measured from here.
    Initialize()
    If phase != 0 || !Core.IsInService()
        Return
    EndIf
    baseMostGold = Game.QueryStat("Most Gold Carried")
    phase = 1
    phaseStart = Utility.GetCurrentGameTime()
    Evaluate()
EndFunction

Int Function GetPhase()
    Return phase
EndFunction

; Conditions

Form Function ResolveForm(Int c)
    Form result = CondForms[c]
    If result == None && CondPlugins[c] != ""
        result = Game.GetFormFromFile(CondFormIDs[c], CondPlugins[c])
    EndIf
    Return result
EndFunction

Bool Function Begun(Quest q)
    Return q != None && (q.IsRunning() || q.IsCompleted() || q.GetStage() > 0)
EndFunction

Bool Function InPlace(Location place, Location target)
    Return place != None && target != None && (place == target || place.IsChild(target))
EndFunction

Int Function CountHeld(ObjectReference holder, Form item)
    ; An item, or any member of a form list.
    FormList choices = item as FormList
    If choices == None
        Return holder.GetItemCount(item)
    EndIf
    Int total = 0
    Int i = 0
    While i < choices.GetSize()
        total += holder.GetItemCount(choices.GetAt(i))
        i += 1
    EndWhile
    Return total
EndFunction

Int Function BestMagic()
    Actor player = Game.GetPlayer()
    Float best = player.GetBaseActorValue("Alteration")
    If player.GetBaseActorValue("Conjuration") > best
        best = player.GetBaseActorValue("Conjuration")
    EndIf
    If player.GetBaseActorValue("Destruction") > best
        best = player.GetBaseActorValue("Destruction")
    EndIf
    If player.GetBaseActorValue("Illusion") > best
        best = player.GetBaseActorValue("Illusion")
    EndIf
    If player.GetBaseActorValue("Restoration") > best
        best = player.GetBaseActorValue("Restoration")
    EndIf
    Return best as Int
EndFunction

Bool Function Check(Int c)
    Int kind = CondKinds[c]
    Int value = CondValues[c]
    Float nowDay = Utility.GetCurrentGameTime()
    If kind == 1
        Return nights >= value
    ElseIf kind == 2
        Return residenceStart > 0.0 && nowDay - residenceStart >= value + delayDays
    ElseIf kind == 3
        Return visited[c]
    ElseIf kind == 15
        Return Game.QueryStat("Most Gold Carried") > baseMostGold
    ElseIf kind == 16
        Return Game.GetPlayer().GetLevel() >= value
    ElseIf kind == 17
        Return BestMagic() >= value
    ElseIf kind == 18
        Return nowDay - phaseStart >= value
    ElseIf kind == 19
        Return phaseWeight >= value
    EndIf
    Form subject = ResolveForm(c)
    If subject == None
        Return kind == 8
    ElseIf kind == 4 || kind == 5
        Return CountHeld(Game.GetPlayer(), subject) >= value
    ElseIf kind == 6
        Return (subject as Quest).GetStageDone(value)
    ElseIf kind == 7
        Return Begun(subject as Quest)
    ElseIf kind == 8
        Return !Begun(subject as Quest)
    ElseIf kind == 9
        Return Game.GetPlayer().IsInFaction(subject as Faction)
    ElseIf kind == 10
        Return (subject as Actor).IsInFaction(CondOtherForms[c] as Faction)
    ElseIf kind == 11
        Return CountHeld(subject as ObjectReference, CondOtherForms[c]) >= value
    ElseIf kind == 12
        Return (subject as Actor).IsDead()
    ElseIf kind == 13
        Return !(subject as Actor).IsDead()
    ElseIf kind == 14
        Return (subject as GlobalVariable).GetValue() >= value
    ElseIf kind == 20
        Return True
    ElseIf kind == 21
        Return (subject as Quest).IsCompleted()
    ElseIf kind == 22
        Return (subject as Quest).GetStage() >= value
    EndIf
    Return False
EndFunction

Bool Function CheckAll(Int first, Int total)
    Int c = first
    While c < first + total
        If !Check(c)
            Return False
        EndIf
        c += 1
    EndWhile
    Return True
EndFunction

; Events from the player alias

Function OnWake()
    ; Sleep events: nights count only at the inn, and only while the residence lasts.
    Initialize()
    If phase == 1 && InPlace(Game.GetPlayer().GetCurrentLocation(), Inn)
        nights += 1
        If residenceStart <= 0.0
            residenceStart = Utility.GetCurrentGameTime()
        EndIf
    EndIf
    Evaluate()
EndFunction

Function RecordVisit(Location place)
    Initialize()
    If phase <= 0 || place == None
        Return
    EndIf
    Int c = 0
    While c < CondKinds.Length
        If CondKinds[c] == 3 && !visited[c] && InPlace(place, CondForms[c] as Location)
            visited[c] = True
        EndIf
        c += 1
    EndWhile
    CheckBounds(place)
    Evaluate()
EndFunction

Function CheckBounds(Location place)
    ; During the residence he may not leave Whiterun or Falkreath. Each absence costs trust and time.
    If phase != 1 || residenceStart <= 0.0
        Return
    EndIf
    Bool inside = False
    Int i = 0
    While i < Bounds.Length && !inside
        inside = InPlace(place, Bounds[i])
        i += 1
    EndWhile
    If inside
        away = False
        Return
    ElseIf away
        Return
    EndIf
    away = True
    delayDays += 3.0
    Core.AdjustTrust(-1)
    Float nowDay = Utility.GetCurrentGameTime()
    If nowDay - lastWanderLetter >= 3.0 && Dispatch.Send(Core.NextTransactionID(), 2899, WanderLetter, Self)
        lastWanderLetter = nowDay
    EndIf
EndFunction

; Issuing

Function Evaluate()
    If phase <= 0
        Return
    EndIf
    Int i = 0
    While i < Orders.Length
        If !issued[i] && Phases[i] == phase && (RequireCond[i] < 0 || Check(RequireCond[i]))
            Issue(i)
        EndIf
        i += 1
    EndWhile
    Int j = 0
    While j < Letters.Length
        If !letterSent[j] && LetterPhases[j] == phase && CheckAll(LetterCondStart[j], LetterCondCount[j])
            Int transactionID = Core.NextTransactionID()
            If Dispatch.Send(transactionID, 2900 + j, Letters[j], Self)
                letterSent[j] = True
                letterTransactions[j] = transactionID
            EndIf
        EndIf
        j += 1
    EndWhile
EndFunction

Function Issue(Int i)
    If Dispatch.ReserveDocument(Orders[i]) < 0 || !Core.RegisterAssignment(2001 + i, 4, 0.0)
        Return
    EndIf
    issued[i] = True
    Dispatch.ArchiveDocument(Orders[i])
    Game.GetPlayer().AddItem(Orders[i], 1, True)
    SetObjectiveDisplayed(100 + i, True)
EndFunction

Function AdvancePhase()
    phase += 1
    phaseStart = Utility.GetCurrentGameTime()
    phaseWeight = 0
    Evaluate()
EndFunction

; Reports

Bool Function IsInstruction(Int i)
    Return i >= 0 && i < Orders.Length
EndFunction

Bool Function FileReport(Int i)
    Initialize()
    lastError = 2
    If !IsInstruction(i)
        Return False
    ElseIf !issued[i]
        Return Reject(0)
    ElseIf !Core.IsOpen(2001 + i) || reportTransactions[i] != 0
        Return Reject(1)
    ElseIf !CheckAll(CondStart[i], CondCount[i])
        notYet = i
        Return Reject(3)
    EndIf
    Bool alt = AltCond[i] >= 0 && Check(AltCond[i])
    Book reply = Replies[i]
    Int outcome = 1
    If alt
        reply = AltReplies[i]
        outcome = 2
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 2001 + i, outcome, Reports[i], reply, Self)
        Return False
    EndIf
    reportTransactions[i] = transactionID
    alternative[i] = alt
    Consume(CondStart[i], CondCount[i])
    Core.RecordFact(2001 + i, 1)
    Core.FileAssignment(2001 + i)
    SetObjectiveDisplayed(100 + i, False)
    SetObjectiveDisplayed(200 + i, True)
    Return True
EndFunction

Function Consume(Int first, Int total)
    ; Deliveries leave his hands once, when the report is accepted.
    Int c = first
    While c < first + total
        If CondKinds[c] == 4
            Form item = ResolveForm(c)
            FormList choices = item as FormList
            If choices == None
                Game.GetPlayer().RemoveItem(item, CondValues[c], True)
            Else
                Int remaining = CondValues[c]
                Int k = 0
                While k < choices.GetSize() && remaining > 0
                    Form member = choices.GetAt(k)
                    Int held = Game.GetPlayer().GetItemCount(member)
                    If held > remaining
                        held = remaining
                    EndIf
                    If held > 0
                        Game.GetPlayer().RemoveItem(member, held, True)
                        remaining -= held
                    EndIf
                    k += 1
                EndWhile
            EndIf
        EndIf
        c += 1
    EndWhile
EndFunction

Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
    If !Dispatch.IsDelivering(transactionID, subjectID, outcome, Self)
        Return
    ElseIf subjectID == 2899
        Return
    ElseIf subjectID >= 2900
        ReceiveLetter(subjectID - 2900, transactionID)
        Return
    EndIf
    Int i = subjectID - 2001
    If !IsInstruction(i) || reportTransactions[i] != transactionID || (outcome != 1 && outcome != 2)
        Return
    EndIf
    If Core.CompleteAssignment(subjectID)
        If alternative[i]
            Core.AdjustTrust(AltTrust[i])
            If Phases[i] == phase
                phaseWeight += AltWeights[i]
            EndIf
        ElseIf Phases[i] == phase
            phaseWeight += Weights[i]
        EndIf
    EndIf
    If Core.GetAssignmentState(subjectID) == 4
        SetObjectiveCompleted(100 + i, True)
        SetObjectiveCompleted(200 + i, True)
    EndIf
    Evaluate()
EndFunction

Function ReceiveLetter(Int j, Int transactionID)
    If j < 0 || j >= Letters.Length || letterTransactions[j] != transactionID || letterDone[j]
        Return
    EndIf
    ; Commit before any inventory call; a replayed callback does nothing.
    letterDone[j] = True
    If EnclosureStart[j] >= 0
        Int k = EnclosureStart[j]
        While k < EnclosureStart[j] + EnclosureCount[j]
            Game.GetPlayer().AddItem(Enclosures[k], 1, True)
            k += 1
        EndWhile
    EndIf
    Int action = LetterActions[j]
    If action == 2
        Core.GrantAuthority(AdvanceOperation, 5, 2)
    ElseIf action == 3
        Core.GrantAuthority(RemovalOperation, 3, 2)
    EndIf
    If action == 1 || action == 2
        AdvancePhase()
    Else
        Evaluate()
    EndIf
EndFunction

; Register and menus

Int Function CountState(Int status)
    Int result = 0
    Int i = 0
    While i < Orders.Length
        If issued[i] && Core.GetAssignmentState(2001 + i) == status
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Int Function ShowSummary()
    Return SummaryMessage.Show(CountState(1), CountState(3), CountState(4), Dispatch.CountResponses(True))
EndFunction

Int Function GetSlotIndex(Int slot)
    ; Menu positions list open instructions: those ready to report first, then the rest,
    ; each in issue order. Eight positions fit the menu; -1 is an empty position.
    If slot < 0
        Return -1
    EndIf
    Int seen = 0
    Int pass = 0
    While pass < 2
        ; Named locals: Caprica v0.3.0 gave both sides of "CheckAll(..) == (pass == 0)" one temporary.
        Bool wantReady = pass == 0
        Int i = 0
        While i < Orders.Length
            Int status = Core.GetAssignmentState(2001 + i)
            Bool ready = False
            If issued[i] && status >= 1 && status <= 3
                ready = CheckAll(CondStart[i], CondCount[i])
            EndIf
            If issued[i] && status >= 1 && status <= 3 && ready == wantReady
                If seen == slot
                    Return i
                EndIf
                seen += 1
            EndIf
            i += 1
        EndWhile
        pass += 1
    EndWhile
    Return -1
EndFunction

Int Function GetSlotAssignment(Int slot)
    Int index = GetSlotIndex(slot)
    If index < 0
        Return 0
    EndIf
    Return 2001 + index
EndFunction

Int Function ChooseInstruction(Message menu)
    Int choice = menu.Show(GetSlotAssignment(0), GetSlotAssignment(1), GetSlotAssignment(2), GetSlotAssignment(3), GetSlotAssignment(4), GetSlotAssignment(5), GetSlotAssignment(6), GetSlotAssignment(7))
    If choice > 7
        Return -1
    EndIf
    Return GetSlotIndex(choice)
EndFunction

Bool Function Reject(Int reason)
    lastError = reason
    Return False
EndFunction

Function ShowFailure()
    If lastError == 3
        NotYetMessages[notYet].Show()
    Else
        FailureMessages[lastError].Show()
    EndIf
EndFunction

Bool Function IsIssued(Int i)
    Return IsInstruction(i) && issued[i]
EndFunction
