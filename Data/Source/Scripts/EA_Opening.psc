Scriptname EA_Opening extends EA_Module
; Alternate Perspective start: released outside Northwatch Keep with a sealed packet.
; Alias 1 is the Northwatch map marker. Opening the packet begins the campaign in Service.

EA_Core Property Core Auto
EA_Dispatch Property Dispatch Auto
EA_Service Property Service Auto
Faction Property NorthwatchFaction Auto
Book Property SealedPacket Auto
; Her letter, civilian papers, the conditional release and the case instructions.
Book[] Property PacketPapers Auto
; Books sent to be read; vanilla titles, not archived.
Form[] Property PacketBooks Auto
Form Property DispatchCase Auto
Form Property Gold Auto
Form Property Dagger Auto
Int Property Allowance = 100 Auto
Bool arrived = False
Bool handoffActive = False
Bool packetOpened = False

Function Fragment_10()
    ; Start-up stage. Alternate Perspective expects the player to leave its cell at once.
    If arrived
        Return
    EndIf
    arrived = True
    Actor player = Game.GetPlayer()
    ; Northwatch completed the handoff; its garrison does not attack a released prisoner.
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
    If (!Core.IsRunning() && !Core.Start()) || (!Dispatch.IsRunning() && !Dispatch.Start()) || (!Service.IsRunning() && !Service.Start())
        packetOpened = False
        Return
    EndIf
    Core.Initialize()
    Dispatch.Initialize()
    ; His service already exists; the packet resumes it under a civilian life.
    Core.Commission()
    Core.SetCoverStatus(True, False)
    Actor player = Game.GetPlayer()
    Int i = 0
    While i < PacketPapers.Length
        player.AddItem(PacketPapers[i], 1, True)
        i += 1
    EndWhile
    i = 0
    While i < PacketBooks.Length
        player.AddItem(PacketBooks[i], 1, True)
        i += 1
    EndWhile
    player.AddItem(Gold, Allowance, True)
    player.AddItem(DispatchCase, 1, True)
    Service.BeginCampaign()
    ; The start ends here; the journal continues with the campaign's own instructions.
    SetObjectiveCompleted(10)
    SetStage(20)
EndFunction
