Scriptname EA_Service extends EA_Module
; Authored instruction packets. Packet index i is assignment 1001 + i.
; Packets are issued in index order; at most three may be uncompleted at once.
; The officer is given directions, not reasons: go to a named place, obtain a named item, report.
; A lead points at a vanilla quest of Thalmor interest. It is read, never advanced: the report
; waits until that quest has begun, however the player chose to pursue it.

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
Book[] Property Orders Auto
Book[] Property Reports Auto
Book[] Property Responses Auto
Book[] Property PromptResponses Auto
Book[] Property LateResponses Auto
Book Property EvaluationRequest Auto
Book[] Property Evaluations Auto
Message[] Property FailureMessages Auto
Message[] Property MissingMessages Auto
Message[] Property StatusMessages Auto
Message Property SummaryMessage Auto
Message Property PacketReadyMessage Auto
Message Property EvaluationQueuedMessage Auto
Book[] Property ExtensionRequests Auto
Book[] Property ApprovedExtensions Auto
Book[] Property DeniedExtensions Auto
Book Property AuthorityRequest Auto
Book Property AuthorityApproved Auto
; Optional packet parts. A per-packet index of -1 means the packet has none.
Int[] Property SupplyIndex Auto
Form[] Property Supplies Auto
Int[] Property SupplyCounts Auto
Int[] Property VisitIndex Auto
Location[] Property Locations Auto
Message[] Property VisitMessages Auto
Int[] Property LeadIndex Auto
Quest[] Property Leads Auto
Message[] Property LeadMessages Auto
Int lastError = 7
Int missingVisit = 0
Int missingLead = 0
Int missingSupply = 0
Int missingCount = 0
Int evaluationTransaction = 0
Bool evaluationDelivered = False
Int notifiedPacket = 0
Int[] reportTransactions
Int[] extensionTransactions
Bool[] extensionUsed
Bool[] extensionDenied
Bool[] visited
Int authorityTransaction = 0
Bool initialized = False
; Failure codes: 0 uncollected, 1 closed, 2 field papers unread, 3 extension pending,
; 4 extension refused, 5 authority pending, 6 authority held, 7 dispatch full,
; 8 named place not visited (VisitMessages), 9 named item short (MissingMessages),
; 10 lead not yet followed (LeadMessages).

Function Initialize()
    If initialized
        Return
    EndIf
    ; Capacity for sixteen packets; Orders.Length is the authored count.
    reportTransactions = new Int[16]
    extensionTransactions = new Int[16]
    extensionUsed = new Bool[16]
    extensionDenied = new Bool[16]
    visited = new Bool[16]
    initialized = True
EndFunction

Bool Function IsPacket(Int selection)
    Return selection >= 0 && selection < Orders.Length
EndFunction

Int Function CountOpen()
    ; Issued and not yet completed, including reports awaiting their response.
    Int result = 0
    Int i = 0
    While i < Orders.Length
        Int status = Core.GetAssignmentState(1001 + i)
        If status >= 1 && status <= 3
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Int Function NextUnissued()
    Int i = 0
    While i < Orders.Length
        If Core.GetAssignmentState(1001 + i) == 0
            Return i
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Function CollectOrders()
    Initialize()
    If !Core.IsInService() || Dispatch.Archive == None
        Return
    EndIf
    Int open = CountOpen()
    Bool blocked = False
    Int i = 0
    While i < Orders.Length
        If Core.GetAssignmentState(1001 + i) == 0
            ; Issue strictly in order: a later packet never overtakes an earlier one.
            If !blocked && open < 3 && IssuePacket(i)
                open += 1
            Else
                blocked = True
            EndIf
        Else
            Dispatch.RecoverDocument(Orders[i])
        EndIf
        i += 1
    EndWhile
    ; Routine investigation does not imply permission to disclose or kill.
    Core.GrantAuthority(1001, 1, 1)
EndFunction

Bool Function IssuePacket(Int index)
    ; Reserve the recovery slot before the assignment exists.
    If Dispatch.ReserveDocument(Orders[index]) < 0
        Return False
    ElseIf !Core.RegisterAssignment(1001 + index, 3, Utility.GetCurrentGameTime() + 10.0)
        Return False
    EndIf
    Dispatch.ArchiveDocument(Orders[index])
    Game.GetPlayer().AddItem(Orders[index], 1, True)
    SetObjectiveDisplayed(100 + index, True)
    If index == 0 && Core.HasReadFieldPapers()
        Core.RecordFact(1001, 1)
    EndIf
    Return True
EndFunction

Int Function CheckFiling(Int selection)
    ; Returns -1 when the report may be filed, otherwise a failure code.
    Int assignmentID = 1001 + selection
    If Core.GetAssignmentState(assignmentID) == 0
        Return 0
    EndIf
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    If !Core.IsOpen(assignmentID) || reportTransactions[selection] != 0
        Return 1
    ElseIf VisitIndex[selection] >= 0 && !visited[selection]
        missingVisit = VisitIndex[selection]
        Return 8
    EndIf
    Int lead = LeadIndex[selection]
    If lead >= 0 && !Leads[lead].IsRunning() && !Leads[lead].IsCompleted()
        missingLead = lead
        Return 10
    EndIf
    Int supply = SupplyIndex[selection]
    If supply >= 0
        missingCount = SupplyCounts[supply] - Game.GetPlayer().GetItemCount(Supplies[supply])
        If missingCount > 0
            missingSupply = supply
            Return 9
        EndIf
    ElseIf !Core.HasFact(assignmentID)
        Return 2
    EndIf
    Return -1
EndFunction

Function RecordVisit(Location place)
    ; Only an arrival after the order was issued counts, and only while it is open.
    Initialize()
    If place == None
        Return
    EndIf
    Int i = 0
    While i < Orders.Length
        Int visit = VisitIndex[i]
        If visit >= 0 && !visited[i] && Core.IsOpen(1001 + i)
            If place == Locations[visit] || place.IsChild(Locations[visit])
                visited[i] = True
                Core.RecordFact(1001 + i, 1)
            EndIf
        EndIf
        i += 1
    EndWhile
EndFunction

Bool Function HasVisited(Int selection)
    Return IsPacket(selection) && visited[selection]
EndFunction

Bool Function FileReport(Int selection)
    Initialize()
    If !IsPacket(selection)
        Return False
    EndIf
    lastError = 7
    Int problem = CheckFiling(selection)
    If problem >= 0
        Return Reject(problem)
    EndIf
    Int assignmentID = 1001 + selection
    Book response = Responses[selection]
    If Core.HasMissedDeadline(assignmentID)
        response = LateResponses[selection]
    ElseIf !extensionUsed[selection] && Core.GetDaysRemaining(assignmentID) >= 5.0
        response = PromptResponses[selection]
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, assignmentID, 1, Reports[selection], response, Self)
        Return False
    EndIf
    reportTransactions[selection] = transactionID
    Int supply = SupplyIndex[selection]
    If supply >= 0
        ; Consign supplies to delivery; the accessible archive stores only papers.
        Game.GetPlayer().RemoveItem(Supplies[supply], SupplyCounts[supply], True)
        Core.RecordFact(assignmentID, 1)
    EndIf
    Core.FileAssignment(assignmentID)
    SetObjectiveDisplayed(100 + selection, False)
    SetObjectiveDisplayed(200 + selection, True)
    Return True
EndFunction

Bool Function RequestExtension(Int selection)
    Initialize()
    lastError = 7
    If !IsPacket(selection)
        Return False
    EndIf
    Int assignmentID = 1001 + selection
    If Core.GetAssignmentState(assignmentID) == 0
        Return Reject(0)
    ElseIf !Core.IsOpen(assignmentID)
        Return Reject(1)
    ElseIf extensionTransactions[selection] != 0
        Return Reject(3)
    ElseIf extensionDenied[selection]
        Return Reject(4)
    EndIf
    Int outcome = 2
    Book reply = ApprovedExtensions[selection]
    If extensionUsed[selection]
        outcome = 3
        reply = DeniedExtensions[selection]
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, assignmentID, outcome, ExtensionRequests[selection], reply, Self)
        Return False
    EndIf
    extensionTransactions[selection] = transactionID
    Return True
EndFunction

Bool Function RequestSupplyAuthority()
    lastError = 7
    If Core.GetAssignmentState(1002) == 0
        Return Reject(0)
    ElseIf !Core.IsOpen(1002)
        Return Reject(1)
    ElseIf authorityTransaction != 0
        Return Reject(5)
    ElseIf Core.GetAuthority(1002, 5) == 2
        Return Reject(6)
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 1002, 4, AuthorityRequest, AuthorityApproved, Self)
        Return False
    EndIf
    authorityTransaction = transactionID
    Return True
EndFunction

Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
    If !Dispatch.IsDelivering(transactionID, subjectID, outcome, Self)
        Return
    EndIf
    If subjectID == 1099 && outcome >= 10 && outcome <= 12 && transactionID == evaluationTransaction
        evaluationDelivered = True
        SetObjectiveCompleted(300, True)
        Return
    EndIf
    Int index = subjectID - 1001
    If !IsPacket(index)
        Return
    EndIf
    If outcome == 1 && reportTransactions[index] == transactionID
        Core.CompleteAssignment(subjectID)
        If Core.GetAssignmentState(subjectID) == 4
            ; Reconcile journal state if a prior callback stopped after Core committed.
            SetObjectiveCompleted(100 + index, True)
            SetObjectiveCompleted(200 + index, True)
        EndIf
    ElseIf (outcome == 2 || outcome == 3) && extensionTransactions[index] == transactionID
        extensionTransactions[index] = 0
        If outcome == 2
            extensionUsed[index] = True
            Core.ExtendAssignment(subjectID, 5.0)
        Else
            extensionDenied[index] = True
        EndIf
    ElseIf outcome == 4 && subjectID == 1002 && authorityTransaction == transactionID
        authorityTransaction = 0
        Core.GrantAuthority(1002, 5, 2)
    EndIf
EndFunction

Int Function CountState(Int status)
    Int result = 0
    Int i = 0
    While i < Orders.Length
        If Core.GetAssignmentState(1001 + i) == status
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Int Function ShowSummary()
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    Return SummaryMessage.Show(CountState(1), CountState(2), CountState(3), CountState(4), Orders.Length, Dispatch.CountResponses(True), Dispatch.CountResponses(False))
EndFunction

Function ShowAssignmentStatus(Int selection)
    If !IsPacket(selection)
        Return
    EndIf
    Int assignmentID = 1001 + selection
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    Int status = Core.GetAssignmentState(assignmentID)
    If status >= 0 && status <= 4
        Float days = Core.GetDaysRemaining(assignmentID)
        If days < 0.0
            days = 0.0 - days
        EndIf
        StatusMessages[status].Show(assignmentID, days)
    EndIf
EndFunction

Int Function GetSlotIndex(Int slot)
    ; Menu positions list open instructions in issue order; -1 is an empty position.
    If slot < 0
        Return -1
    EndIf
    Int seen = 0
    Int i = 0
    While i < Orders.Length
        Int status = Core.GetAssignmentState(1001 + i)
        If status >= 1 && status <= 3
            If seen == slot
                Return i
            EndIf
            seen += 1
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Int Function GetSlotAssignment(Int slot)
    Int index = GetSlotIndex(slot)
    If index < 0
        Return 0
    EndIf
    Return 1001 + index
EndFunction

Int Function ChooseInstruction(Message menu)
    Int choice = menu.Show(GetSlotAssignment(0), GetSlotAssignment(1), GetSlotAssignment(2))
    If choice > 2
        Return -1
    EndIf
    Return GetSlotIndex(choice)
EndFunction

Bool Function Reject(Int reason)
    lastError = reason
    Return False
EndFunction

Function ShowFailure()
    If lastError == 8
        VisitMessages[missingVisit].Show()
    ElseIf lastError == 9
        MissingMessages[missingSupply].Show(missingCount)
    ElseIf lastError == 10
        LeadMessages[missingLead].Show()
    Else
        FailureMessages[lastError].Show()
    EndIf
EndFunction

Function CheckPacketNotice()
    Int next = NextUnissued()
    If next > notifiedPacket && CountOpen() < 3
        notifiedPacket = next
        PacketReadyMessage.Show()
    EndIf
EndFunction

Bool Function TryQueueEvaluation(Int financialConcern, Bool accountsPending)
    ; Controller supplies the Accounts snapshot, preserving the plugin dependency graph.
    If evaluationTransaction != 0 || CountState(4) != Orders.Length || accountsPending
        Return False
    EndIf
    Int faults = 0
    Int i = 0
    While i < Orders.Length
        If Core.HasMissedDeadline(1001 + i)
            faults += 1
        EndIf
        i += 1
    EndWhile
    Int assessment = 0
    If faults >= 2 || financialConcern >= 2
        assessment = 2
    ElseIf faults > 0 || financialConcern == 1
        assessment = 1
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 1099, 10 + assessment, EvaluationRequest, Evaluations[assessment], Self)
        Return False
    EndIf
    evaluationTransaction = transactionID
    SetObjectiveDisplayed(300, True)
    EvaluationQueuedMessage.Show()
    Return True
EndFunction

Int Function GetEvaluationState()
    If evaluationDelivered
        Return 2
    ElseIf evaluationTransaction > 0
        Return 1
    EndIf
    Return 0
EndFunction
