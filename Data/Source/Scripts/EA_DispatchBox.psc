Scriptname EA_DispatchBox extends ObjectReference
EA_Prototype Property Controller Auto

Event OnActivate(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        If Controller.IsRunning() || Controller.Start()
            Controller.UseBox(Self)
        Else
            Debug.Notification("The dispatch box is unavailable.")
        EndIf
    EndIf
EndEvent
