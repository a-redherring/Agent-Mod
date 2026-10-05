Scriptname EA_Accounts extends EA_Module
; Prototype case ledger: a single supply operation, one advance and one claim.
; This bounded pilot deliberately does not present itself as a banking system.

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
Form Property Gold Auto
Book Property AdvanceReceipt Auto
Book Property ReturnReceipt Auto
Book Property AuditNotice Auto
Book[] Property ClaimForms Auto
Book[] Property Decisions Auto
Book Property ExplanationForm Auto
Book Property PersonalExplanationForm Auto
Book Property MealPartialDecision Auto
Message Property BalanceMessage Auto
Message[] Property FailureMessages Auto
Int lastError = 10
Bool auditIssue = False

Bool advanceIssued = False
Float advanceDate = 0.0
Int advanceOutstanding = 0
Int operationalDebt = 0
Int creditworthiness = 50
Bool financialProbation = False
Bool audited = False
Float expenseDate = 0.0
Int expenseOperation = 0
String expensePayee = ""
String expenseService = ""
Int expenseAmount = 0
Int claimAmount = 0
Int claimCategory = -1
Int claimTransaction = 0
Int claimState = 0
Float claimArrivalDay = 0.0
Int amountAllowed = 0
Int amountReimbursed = 0
Int personalCost = 0
; Claim states: 0 absent, 1 in transit, 2 settled, 3 returned, 4 explanation in transit.
; Outcomes: 1 approved, 2 partial, 3 denied, 4 returned for explanation.

Bool Function IssueAdvance()
    If advanceIssued
        Return Reject(0)
    ElseIf financialProbation || creditworthiness < 25
        Return Reject(1)
    ElseIf !Core.IsOpen(1002)
        Return Reject(2)
    ElseIf Core.GetAuthority(1002, 5) != 2
        Return Reject(3)
    EndIf
    advanceIssued = True
    advanceDate = Utility.GetCurrentGameTime()
    advanceOutstanding = 80
    Game.GetPlayer().AddItem(Gold, 80, True)
    Game.GetPlayer().AddItem(AdvanceReceipt, 1, True)
    Dispatch.ArchiveDocument(AdvanceReceipt)
    Return True
EndFunction

Bool Function SubmitClaim(Int selection)
    ; Costs are explicitly declared on authored forms, never inferred from inventory.
    Int assignmentState = Core.GetAssignmentState(1002)
    lastError = 10
    If selection < 0 || selection > 3
        Return False
    ElseIf claimState == 1 || claimState == 4
        Return Reject(5)
    ElseIf claimState == 2
        Return Reject(6)
    ElseIf claimState == 3
        Return Reject(7)
    ElseIf assignmentState != 3 && assignmentState != 4
        Return Reject(4)
    EndIf
    Int outcome = selection + 1
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 1002, outcome, ClaimForms[selection], Decisions[selection], Self)
        Return False
    EndIf
    claimTransaction = transactionID
    claimCategory = selection
    expenseDate = Utility.GetCurrentGameTime()
    expenseOperation = 1002
    expensePayee = "Supplier declared on claim form"
    expenseService = "Alto wine procurement"
    expenseAmount = 30
    If selection == 1
        expenseAmount = 80
    ElseIf selection == 2
        expenseService = "Personal gift"
    ElseIf selection == 3
        expenseService = "Meal; explanation requested"
    EndIf
    claimAmount = expenseAmount
    claimState = 1
    claimArrivalDay = Utility.GetCurrentGameTime() + 1.0
    Return True
EndFunction

Bool Function ExplainClaim(Bool operationalPurpose)
    lastError = 10
    If claimState == 1 || claimState == 4
        Return Reject(5)
    ElseIf claimState == 2
        Return Reject(6)
    ElseIf claimState != 3
        Return Reject(7)
    EndIf
    Int outcome = 3
    Book explanation = PersonalExplanationForm
    Book decision = Decisions[2]
    If operationalPurpose
        outcome = 2
        explanation = ExplanationForm
        decision = MealPartialDecision
    EndIf
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 1002, outcome, explanation, decision, Self)
        Return False
    EndIf
    claimTransaction = transactionID
    claimState = 4
    claimArrivalDay = Utility.GetCurrentGameTime() + 1.0
    Return True
EndFunction

Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
    If !Dispatch.IsDelivering(transactionID, subjectID, outcome, Self)
        Return
    EndIf
    If transactionID != claimTransaction || subjectID != expenseOperation || (claimState != 1 && claimState != 4)
        Return
    EndIf
    If outcome == 4 && claimState == 1
        claimState = 3
        Return
    EndIf
    Int allowed = 0
    If outcome == 1
        allowed = claimAmount
    ElseIf outcome == 2
        allowed = 30
        If claimState == 4
            allowed = 15
        EndIf
    ElseIf outcome != 3
        Return
    EndIf
    ; Commit the settlement before inventory calls. A callback replay is a no-op.
    claimState = 2
    amountAllowed = allowed
    personalCost = claimAmount - allowed
    Int funded = claimAmount
    If funded > advanceOutstanding
        funded = advanceOutstanding
    EndIf
    advanceOutstanding -= funded
    Int cash = allowed - funded
    If cash < 0
        operationalDebt -= cash
        cash = 0
    EndIf
    ; Recognized expenses first discharge audited liability from this operation.
    Int discharge = operationalDebt
    If discharge > cash
        discharge = cash
    EndIf
    operationalDebt -= discharge
    cash -= discharge
    amountReimbursed = cash
    If cash > 0
        Game.GetPlayer().AddItem(Gold, cash, True)
    EndIf
    If outcome == 3
        Core.AdjustTrust(-1)
        creditworthiness -= 10
    EndIf
    RefreshProbation()
EndFunction

Int Function ReturnFunds()
    Return ReturnAmount(0)
EndFunction

Int Function ReturnAmount(Int maximum)
    ; Zero means all affordable outstanding funds; a negative amount is invalid.
    lastError = 10
    If maximum < 0
        Return 0
    EndIf
    Int available = Game.GetPlayer().GetItemCount(Gold)
    Int returned = GetOutstanding()
    If returned <= 0
        lastError = 8
        Return 0
    ElseIf available <= 0
        lastError = 9
        Return 0
    EndIf
    If maximum > 0 && returned > maximum
        returned = maximum
    EndIf
    If available < returned
        returned = available
    EndIf
    If returned <= 0
        Return 0
    EndIf
    Int advancePart = returned
    If advancePart > advanceOutstanding
        advancePart = advanceOutstanding
    EndIf
    advanceOutstanding -= advancePart
    operationalDebt -= returned - advancePart
    Game.GetPlayer().RemoveItem(Gold, returned, True)
    Game.GetPlayer().AddItem(ReturnReceipt, 1, True)
    Dispatch.ArchiveDocument(ReturnReceipt)
    RefreshProbation()
    Return returned
EndFunction

Function Audit()
    If audited || !advanceIssued
        Return
    EndIf
    Float nowDay = Utility.GetCurrentGameTime()
    If nowDay <= advanceDate + 14.0
        Return
    EndIf
    ; Defer only during actual transit, never indefinitely for an unread response.
    If (claimState == 1 || claimState == 4) && nowDay < claimArrivalDay
        Return
    EndIf
    audited = True
    If advanceOutstanding > 0
        auditIssue = True
        operationalDebt += advanceOutstanding
        advanceOutstanding = 0
        creditworthiness -= 10
        Game.GetPlayer().AddItem(AuditNotice, 1, True)
        Dispatch.ArchiveDocument(AuditNotice)
    EndIf
    RefreshProbation()
EndFunction

Function RefreshProbation()
    financialProbation = operationalDebt > 0
    If operationalDebt == 0 && advanceOutstanding == 0 && advanceIssued
        creditworthiness = 50
    EndIf
EndFunction

Function ShowStatement()
    ; Actual money fields are appropriate to a statement; hidden trust is never shown.
    BalanceMessage.Show(advanceOutstanding, operationalDebt, amountAllowed, amountReimbursed)
EndFunction

Bool Function NeedsExplanation()
    Return claimState == 3
EndFunction

Function TraceLedger()
    Core.Trace("Expense day " + expenseDate + ", operation " + expenseOperation + ", payee " + expensePayee)
    Core.Trace("Service " + expenseService + ", category " + claimCategory + ", declared " + expenseAmount)
    Core.Trace("Personal cost " + personalCost + ", reimbursed " + amountReimbursed)
EndFunction

Int Function GetOutstanding()
    Return advanceOutstanding + operationalDebt
EndFunction

Bool Function IsReviewPending()
    Return claimState == 1 || claimState == 3 || claimState == 4
EndFunction

Int Function GetReviewConcern()
    If GetOutstanding() > 0 || auditIssue || (claimState == 2 && amountAllowed == 0)
        Return 2
    ElseIf claimState == 2 && personalCost > 0
        Return 1
    EndIf
    Return 0
EndFunction

Bool Function Reject(Int reason)
    lastError = reason
    Return False
EndFunction

Function ShowFailure()
    FailureMessages[lastError].Show()
EndFunction
