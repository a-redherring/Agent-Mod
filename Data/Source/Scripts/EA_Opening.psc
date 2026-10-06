Scriptname EA_Opening extends EA_Module
; Alternate Perspective start: released outside Northwatch Keep into civilian cover.
; Alias 1 is the Northwatch map marker. Establish Cover is Core assignment 900.

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
Faction Property NorthwatchFaction Auto
; Companions, College of Winterhold, Thieves Guild: membership and quarters. Bards College: membership only.
Faction[] Property GuildFactions Auto
Book Property SealedPacket Auto
Book Property ArrivalLetter Auto
Book Property CivilianPapers Auto
Book Property DispatchInstructions Auto
Book Property ReportForm Auto
Book Property FieldPapers Auto
Book[] Property Reports Auto
Book[] Property Responses Auto
Form Property DispatchCase Auto
Form Property Gold Auto
Form Property Dagger Auto
Message Property OccupationMenu Auto
Message Property LodgingMenu Auto
Message Property AttestationMenu Auto
Message Property FiledMessage Auto
Message Property ClosedMessage Auto
Message Property IncomeMessage Auto
Message[] Property EvidenceMessages Auto
Message[] Property LodgingMessages Auto
Bool arrived = False
Bool handoffActive = False
Bool packetOpened = False
Bool coverAccepted = False
Int reportTransaction = 0
Int occupation = -1
; Statistics when the packet was opened. Evidence of a cover must postdate arrival.
Int baseMade = 0
Int baseAnimals = 0
Int baseWork = 0
Int baseStudy = 0
Int baseSlept = 0
Int baseMostGold = 0
; Occupations: 0 guild, 1 trade or craft, 2 hunting, 3 paid work, 4 study.
; Lodgings: 0 rented room, 1 own house, 2 guild quarters.

Function Fragment_10()
    ; Start-up stage. Alternate Perspective expects the player to leave its cell at once.
    If arrived
        Return
    EndIf
    arrived = True
    Actor player = Game.GetPlayer()
    ; Northwatch completed the handoff; its garrison does not attack a released transfer.
    player.AddToFaction(NorthwatchFaction)
    player.StopCombatAlarm()
    handoffActive = True
    player.MoveTo(GetArrival())
    player.AddItem(Dagger, 1, True)
    player.AddItem(SealedPacket, 1, True)
    SetObjectiveDisplayed(10)
    RegisterForSingleUpdate(5.0)
EndFunction

ObjectReference Function GetArrival()
    Return (GetAlias(1) as ReferenceAlias).GetReference()
EndFunction

Event OnUpdate()
    ; The courtesy lasts only until the player leaves; Northwatch's own quest is unchanged.
    If !handoffActive
        Return
    EndIf
    If Game.GetPlayer().GetDistance(GetArrival()) < 4096.0
        RegisterForSingleUpdate(5.0)
        Return
    EndIf
    handoffActive = False
    Game.GetPlayer().RemoveFromFaction(NorthwatchFaction)
EndEvent

Function OpenPacket()
    If !arrived || packetOpened
        Return
    EndIf
    packetOpened = True
    If (!Core.IsRunning() && !Core.Start()) || (!Dispatch.IsRunning() && !Dispatch.Start())
        packetOpened = False
        Return
    EndIf
    Core.Initialize()
    Dispatch.Initialize()
    ; The service already exists; opening the packet resumes it under civilian cover.
    Core.Commission()
    Core.SetOpening(Self)
    Core.RegisterAssignment(900, 1, 0.0)
    Actor player = Game.GetPlayer()
    player.AddItem(ArrivalLetter, 1, True)
    player.AddItem(CivilianPapers, 1, True)
    player.AddItem(DispatchInstructions, 1, True)
    player.AddItem(ReportForm, 1, True)
    player.AddItem(Gold, 100, True)
    player.AddItem(DispatchCase, 1, True)
    baseMade = Made()
    baseAnimals = Game.QueryStat("Animals Killed")
    baseWork = Work()
    baseStudy = Study()
    baseSlept = Game.QueryStat("Hours Slept")
    baseMostGold = Game.QueryStat("Most Gold Carried")
    SetObjectiveCompleted(10)
    SetStage(20)
    SetObjectiveDisplayed(20)
    SetObjectiveDisplayed(21)
    SetObjectiveDisplayed(22)
    SetObjectiveDisplayed(23)
EndFunction

Int Function Made()
    Return Game.QueryStat("Weapons Made") + Game.QueryStat("Armor Made") + Game.QueryStat("Potions Mixed") + Game.QueryStat("Magic Items Made")
EndFunction

Int Function Work()
    Return Game.QueryStat("Quests Completed") + Game.QueryStat("Misc Objectives Completed")
EndFunction

Int Function Study()
    Return Game.QueryStat("Skill Books Read") + Game.QueryStat("Spells Learned") + Game.QueryStat("Training Sessions")
EndFunction

Bool Function InGuild(Int count)
    ; The first count factions are checked; quarters exist only for the first three.
    Actor player = Game.GetPlayer()
    Int i = 0
    While i < count && i < GuildFactions.Length
        If player.IsInFaction(GuildFactions[i])
            Return True
        EndIf
        i += 1
    EndWhile
    Return False
EndFunction

Bool Function HasOccupation(Int choice)
    If choice == 0
        Return InGuild(GuildFactions.Length)
    ElseIf choice == 1
        Return Made() - baseMade >= 3
    ElseIf choice == 2
        Return Game.QueryStat("Animals Killed") - baseAnimals >= 5
    ElseIf choice == 3
        Return Work() - baseWork >= 1
    ElseIf choice == 4
        Return Study() - baseStudy >= 2
    EndIf
    Return False
EndFunction

Bool Function HasLodging(Int choice, Int work)
    If choice == 0
        Return Game.QueryStat("Hours Slept") - baseSlept >= 1
    ElseIf choice == 1
        Return Game.QueryStat("Houses Owned") >= 1
    ElseIf choice == 2
        Return work == 0 && InGuild(3)
    EndIf
    Return False
EndFunction

Bool Function FileCoverReport()
    If !packetOpened
        Return False
    ElseIf reportTransaction != 0
        ClosedMessage.Show()
        Return False
    EndIf
    Int work = OccupationMenu.Show()
    If work < 0 || work > 4
        Return False
    ElseIf !HasOccupation(work)
        EvidenceMessages[work].Show()
        Return False
    EndIf
    Int lodging = LodgingMenu.Show()
    If lodging < 0 || lodging > 2
        Return False
    ElseIf !HasLodging(lodging, work)
        LodgingMessages[lodging].Show()
        Return False
    ElseIf Game.QueryStat("Most Gold Carried") <= baseMostGold
        ; Carrying more than ever before is the plainest sign of money that is not Elenwen's.
        IncomeMessage.Show()
        Return False
    ElseIf AttestationMenu.Show() != 0
        Return False
    EndIf
    Core.RecordFact(900, 1)
    Int transactionID = Core.NextTransactionID()
    If !Dispatch.Queue(transactionID, 900, 1, Reports[work], Responses[work], Self)
        Return False
    EndIf
    reportTransaction = transactionID
    occupation = work
    Core.FileAssignment(900)
    SetObjectiveCompleted(20)
    SetObjectiveCompleted(21)
    SetObjectiveCompleted(22)
    SetObjectiveCompleted(23)
    SetStage(30)
    SetObjectiveDisplayed(30)
    FiledMessage.Show()
    Return True
EndFunction

Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
    If !Dispatch.IsDelivering(transactionID, subjectID, outcome, Self)
        Return
    ElseIf subjectID != 900 || outcome != 1 || transactionID != reportTransaction || coverAccepted
        Return
    EndIf
    coverAccepted = True
    Core.CompleteAssignment(900)
    Core.SetCoverStatus(True, False)
    ; Procedure papers follow acceptance; orders are collected from the case.
    Game.GetPlayer().AddItem(FieldPapers, 1, True)
    Dispatch.ArchiveDocument(FieldPapers)
    SetObjectiveCompleted(30)
    SetStage(40)
EndFunction

Bool Function IsCoverAccepted()
    Return coverAccepted
EndFunction

Int Function GetOccupation()
    Return occupation
EndFunction
