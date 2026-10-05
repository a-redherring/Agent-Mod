Scriptname EA_Prototype extends Quest

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
EA_Service Property Service Auto
EA_Accounts Property Accounts Auto
Form Property Gold Auto
Book Property Commission Auto
Book Property FieldPapers Auto
Container Property ArchiveBase Auto
Message Property CommissionMenu Auto
Message Property MainMenu Auto
Message Property AssignmentMenu Auto
Message Property AccountsMenu Auto
Message Property ClaimMenu Auto
Message Property ExplanationMenu Auto
Message Property FiledMessage Auto
Message Property UnavailableMessage Auto
Message Property CollectedMessage Auto
Message Property RepaymentMenu Auto
Message Property ReturnedMessage Auto
Message Property ReviewPendingMessage Auto
Bool supplied = False
ObjectReference activeBox

Function UseBox(ObjectReference box)
    ; All player mutations run through this serialized physical interaction.
    ; No console command is needed after the prototype box has been placed.
    GoToState("Busy")
    If activeBox == None
        activeBox = box
    EndIf
    If (!Core.IsRunning() && !Core.Start()) || (!Dispatch.IsRunning() && !Dispatch.Start()) || (!Service.IsRunning() && !Service.Start()) || (!Accounts.IsRunning() && !Accounts.Start())
        Debug.Trace("[EA] Framework quest startup failed; no player transaction performed.")
        UnavailableMessage.Show()
        GoToState("")
        Return
    EndIf
    Core.Initialize()
    Dispatch.Initialize()
    Service.Initialize()
    If !Core.IsInService()
        If CommissionMenu.Show() != 0
            GoToState("")
            Return
        EndIf
        Core.Commission()
    EndIf
    If Dispatch.Archive == None
        Dispatch.Archive = box.PlaceAtMe(ArchiveBase, 1, True, False)
        If Dispatch.Archive == None
            UnavailableMessage.Show()
            GoToState("")
            Return
        EndIf
        Dispatch.Archive.MoveTo(box, 65.0, 0.0, 0.0)
    EndIf
    If !supplied
        supplied = True
        Game.GetPlayer().AddItem(Commission, 1, True)
        Game.GetPlayer().AddItem(FieldPapers, 1, True)
        Game.GetPlayer().AddItem(Gold, 100, True)
        Dispatch.ArchiveDocument(Commission)
        Dispatch.ArchiveDocument(FieldPapers)
    EndIf
    Core.RefreshDeadlines(Utility.GetCurrentGameTime())
    Dispatch.ScheduleNext()
    Accounts.Audit()
    Service.TryQueueEvaluation(Accounts.GetReviewConcern(), Accounts.IsReviewPending())
    Int selected = MainMenu.Show()
    Int assignment = -1
    If selected == 0
        Service.CollectOrders()
        Dispatch.RecoverDocument(Commission)
        Dispatch.RecoverDocument(FieldPapers)
    ElseIf selected == 1
        assignment = Service.ChooseInstruction(AssignmentMenu)
        If assignment >= 0
            FileReport(assignment)
        EndIf
    ElseIf selected == 2
        assignment = Service.ChooseInstruction(AssignmentMenu)
        If assignment >= 0
            ShowServiceResult(Service.RequestExtension(assignment))
        EndIf
    ElseIf selected == 3
        ShowServiceResult(Service.RequestSupplyAuthority())
    ElseIf selected == 4
        UseAccounts()
    ElseIf selected == 5
        CollectedMessage.Show(Dispatch.CollectResponses())
        Service.CheckPacketNotice()
    ElseIf selected == 6
        Dispatch.RecoverFiledCopies()
    ElseIf selected == 7
        If Service.ShowSummary() == 0
            assignment = Service.ChooseInstruction(AssignmentMenu)
            If assignment >= 0
                Service.ShowAssignmentStatus(assignment)
            EndIf
        EndIf
        If Service.CountOpen() == 0 && Service.NextUnissued() < 0 && Service.GetEvaluationState() == 0 && Accounts.IsReviewPending()
            ReviewPendingMessage.Show()
        EndIf
    EndIf
    Service.TryQueueEvaluation(Accounts.GetReviewConcern(), Accounts.IsReviewPending())
    GoToState("")
EndFunction

Function UseAccounts()
    Int selected = AccountsMenu.Show()
    If selected == 0
        ShowAccountsResult(Accounts.IssueAdvance())
    ElseIf selected == 1
        If Accounts.NeedsExplanation()
            Int explanation = ExplanationMenu.Show()
            If explanation >= 0 && explanation < 2
                ShowAccountsResult(Accounts.ExplainClaim(explanation == 0))
            EndIf
        Else
            Int claim = ClaimMenu.Show()
            If claim >= 0 && claim < 4
                ShowAccountsResult(Accounts.SubmitClaim(claim))
            EndIf
        EndIf
    ElseIf selected == 2
        Int repayment = RepaymentMenu.Show()
        If repayment >= 0 && repayment < 3
            Int maximum = 0
            If repayment == 0
                maximum = 10
            ElseIf repayment == 1
                maximum = 25
            EndIf
            Int returned = Accounts.ReturnAmount(maximum)
            If returned > 0
                ReturnedMessage.Show(returned, Accounts.GetOutstanding())
            Else
                Accounts.ShowFailure()
            EndIf
        EndIf
    ElseIf selected == 3
        Accounts.ShowStatement()
    EndIf
EndFunction

Function FileReport(Int assignment)
    ; A case report needs one conclusion, asked only once the papers and supplies are in order.
    If Service.IsReadyForConclusion(assignment)
        Int conclusion = Service.AskConclusion(assignment)
        If conclusion >= 0
            ShowServiceResult(Service.FileReport(assignment, conclusion))
        EndIf
    Else
        ShowServiceResult(Service.FileReport(assignment, -1))
    EndIf
EndFunction

Function ShowServiceResult(Bool accepted)
    If accepted
        FiledMessage.Show()
    Else
        Service.ShowFailure()
    EndIf
EndFunction

Function ShowAccountsResult(Bool accepted)
    If accepted
        FiledMessage.Show()
    Else
        Accounts.ShowFailure()
    EndIf
EndFunction

State Busy
    Function UseBox(ObjectReference box)
        ; Ignore concurrent activation, including from a second test box.
    EndFunction
EndState
