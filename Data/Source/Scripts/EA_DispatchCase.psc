Scriptname EA_DispatchCase extends ObjectReference
; Set down outside any container, the packed case opens into the dispatch box.
EA_Prototype Property Controller Auto

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
    If akNewContainer == None && akOldContainer == Game.GetPlayer()
        ; Let a dropped case come to rest before the box takes its place.
        Utility.Wait(1.0)
        If Controller.IsRunning() || Controller.Start()
            Controller.Unpack(Self)
        EndIf
    EndIf
EndEvent
