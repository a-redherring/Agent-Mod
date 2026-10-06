Scriptname EA_Prototype extends Quest

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
EA_Service Property Service Auto
EA_Accounts Property Accounts Auto
Form Property Gold Auto
Book Property Commission Auto
Container Property ArchiveBase Auto
Activator Property BoxBase Auto
MiscObject Property CaseItem Auto
Message Property CaseMenu Auto
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
Bool supplied = False
ObjectReference activeBox

Function UseBox(ObjectReference box)
    ; All player mutations run through this serialized physical interaction.
    ; The box is set down from the dispatch case, or placed by console for prototype tests.
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
        ; Console path only: the Alternate Perspective start commissions through the packet.
        If CommissionMenu.Show() != 0
            GoToState("")
            Return
        EndIf
        Core.Commission()
        Core.SetCoverStatus(True, False)
        supplied = True
        Game.GetPlayer().AddItem(Commission, 1, True)
        Game.GetPlayer().AddItem(Gold, 100, True)
    EndIf
    If Dispatch.Archive == None
        Dispatch.Archive = box.PlaceAtMe(ArchiveBase, 1, True, False)
        If Dispatch.Archive == None
            UnavailableMessage.Show()
            GoToState("")
            Return
        EndIf
        Dispatch.Archive.MoveTo(box, 65.0, 0.0, 0.0)
        If supplied
            Dispatch.ArchiveDocument(Commission)
        EndIf
    EndIf
    Service.BeginCampaign()
    Dispatch.ScheduleNext()
    Accounts.Audit()
    Int selected = MainMenu.Show()
    Int assignment = -1
    If selected == 0
        assignment = Service.ChooseInstruction(AssignmentMenu)
        If assignment >= 0
            ShowServiceResult(Service.FileReport(assignment))
        EndIf
    ElseIf selected == 1
        CollectedMessage.Show(Dispatch.CollectResponses())
    ElseIf selected == 2
        UseAccounts()
    ElseIf selected == 3
        Service.ShowSummary()
    ElseIf selected == 4
        UseCase(box)
    EndIf
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

Function UseCase(ObjectReference box)
    Int selected = CaseMenu.Show()
    If selected == 0
        If Dispatch.Archive != None
            Dispatch.Archive.Activate(Game.GetPlayer())
        EndIf
    ElseIf selected == 1
        Dispatch.RecoverFiledCopies()
    ElseIf selected == 2
        PackCase(box)
    EndIf
EndFunction

Function PackCase(ObjectReference box)
    ; Filed papers stay with the case; the archive is hidden until it is set down again.
    Game.GetPlayer().AddItem(CaseItem, 1, True)
    If Dispatch.Archive != None
        Dispatch.Archive.Disable()
    EndIf
    If activeBox == box
        activeBox = None
    EndIf
    box.Disable()
    box.Delete()
EndFunction

Function Unpack(ObjectReference caseRef)
    ; The case becomes the dispatch box where it was set down.
    ObjectReference box = caseRef.PlaceAtMe(BoxBase, 1, True, False)
    caseRef.Disable()
    caseRef.Delete()
    If Dispatch.Archive != None
        Dispatch.Archive.MoveTo(box, 65.0, 0.0, 0.0)
        Dispatch.Archive.Enable()
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
