Scriptname EA_Service extends EA_Module

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
Form Property Wine Auto
Form Property Flowers Auto
Form Property Firewood Auto
Form Property LeatherStrips Auto
Form Property Wheat Auto
Int lastError = 7
Int missingSelection = 0
Int missingCount = 0
Int evaluationTransaction = 0
Bool evaluationDelivered = False
Bool packetNotified = False
Int[] reportTransactions
Int[] extensionTransactions
Bool[] extensionUsed
Bool[] extensionDenied
Int authorityTransaction = 0
Bool initialized = False

Function Initialize()
    If initialized
        Return
    EndIf
    reportTransactions = new Int[6]
    extensionTransactions = new Int[6]
    extensionUsed = new Bool[6]
    extensionDenied = new Bool[6]
    initialized = True
EndFunction

Function CollectOrders()
    Initialize()
    If !Core.IsInService() || Dispatch.Archive == None
        Return
    EndIf
    Int limit = 3
    If FirstPacketComplete()
        limit = 6
    EndIf
    Int i = 0
    While i < limit
        Int assignmentID = 1001 + i
        If Core.GetAssignmentState(assignmentID) == 0
            If Dispatch.ReserveDocument(Orders[i]) >= 0 && Core.RegisterAssignment(assignmentID, 3, Utility.GetCurrentGameTime() + 10.0)
                Dispatch.ArchiveDocument(Orders[i])
                Game.GetPlayer().AddItem(Orders[i], 1, True)
                SetObjectiveDisplayed(10 + i, True)
                If i == 0 && Core.HasReadFieldPapers()
                    Core.RecordFact(1001, 1)
                EndIf
            EndIf
        Else
            Dispatch.RecoverDocument(Orders[i])
        EndIf
        i += 1
    EndWhile
    ; Routine investigation does not imply permission to disclose or kill.
    Core.GrantAuthority(1001, 1, 1)
EndFunction

Bool Function FileReport(Int selection)
    Initialize()
    If selection < 0 || selection > 5
        Return False
    EndIf
    lastError = 7
    Int assignmentID = 1001 + selection
    If Core.GetAssignmentState(assignmentID) == 0
        Return Reject(0)
    EndIf
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    If !Core.IsOpen(assignmentID) || reportTransactions[selection] != 0
        Return Reject(1)
    EndIf
    Form supplies = None
    Int quantity = 0
    If selection == 1
        supplies = Wine
        quantity = 3
    ElseIf selection == 2
        supplies = Flowers
        quantity = 6
    ElseIf selection == 3
        supplies = Firewood
        quantity = 6
    ElseIf selection == 4
        supplies = LeatherStrips
        quantity = 4
    ElseIf selection == 5
        supplies = Wheat
        quantity = 6
    EndIf
    If supplies != None
        missingCount = quantity - Game.GetPlayer().GetItemCount(supplies)
        If missingCount > 0
            missingSelection = selection
            Return Reject(8)
        EndIf
    ElseIf !Core.HasFact(assignmentID)
        Return Reject(2)
    EndIf
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
    If supplies != None
        ; Consign supplies to delivery; the accessible archive stores only papers.
        Game.GetPlayer().RemoveItem(supplies, quantity, True)
        Core.RecordFact(assignmentID, 1)
    EndIf
    Core.FileAssignment(assignmentID)
    SetObjectiveDisplayed(10 + selection, False)
    SetObjectiveDisplayed(20 + selection, True)
    Return True
EndFunction

Bool Function RequestExtension(Int selection)
    Initialize()
    lastError = 7
    If selection < 0 || selection > 5
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
        SetObjectiveCompleted(30, True)
        Return
    EndIf
    Int index = subjectID - 1001
    If index < 0 || index > 5
        Return
    EndIf
    If outcome == 1 && reportTransactions[index] == transactionID
        Core.CompleteAssignment(subjectID)
        If Core.GetAssignmentState(subjectID) == 4
            ; Reconcile journal state if a prior callback stopped after Core committed.
            SetObjectiveCompleted(10 + index, True)
            SetObjectiveCompleted(20 + index, True)
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

Bool Function FirstPacketComplete()
    Return Core.GetAssignmentState(1001) == 4 && Core.GetAssignmentState(1002) == 4 && Core.GetAssignmentState(1003) == 4
EndFunction

Int Function CountState(Int status)
    Int result = 0
    Int i = 0
    While i < 6
        If Core.GetAssignmentState(1001 + i) == status
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Int Function ShowSummary()
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    Return SummaryMessage.Show(CountState(1), CountState(2), CountState(3), CountState(4), Dispatch.CountResponses(True), Dispatch.CountResponses(False))
EndFunction

Function ShowAssignmentStatus(Int selection)
    If selection < 0 || selection > 5
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

Bool Function Reject(Int reason)
    lastError = reason
    Return False
EndFunction

Function ShowFailure()
    If lastError == 8
        MissingMessages[missingSelection].Show(missingCount)
    Else
        FailureMessages[lastError].Show()
    EndIf
EndFunction

Function CheckPacketNotice()
    If !packetNotified && FirstPacketComplete() && Core.GetAssignmentState(1004) == 0
        packetNotified = True
        PacketReadyMessage.Show()
    EndIf
EndFunction

Bool Function TryQueueEvaluation(Int financialConcern, Bool accountsPending)
    ; Controller supplies the Accounts snapshot, preserving the plugin dependency graph.
    If evaluationTransaction != 0 || CountState(4) != 6 || accountsPending
        Return False
    EndIf
    Int late = 0
    Int i = 0
    While i < 6
        If Core.HasMissedDeadline(1001 + i)
            late += 1
        EndIf
        i += 1
    EndWhile
    Int assessment = 0
    If late >= 2 || financialConcern >= 2
        assessment = 2
    ElseIf late > 0 || financialConcern == 1
        assessment = 1
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 1099, 10 + assessment, EvaluationRequest, Evaluations[assessment], Self)
        Return False
    EndIf
    evaluationTransaction = transactionID
    SetObjectiveDisplayed(30, True)
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
