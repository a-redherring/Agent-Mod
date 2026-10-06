Scriptname EA_ServicePlayer extends ReferenceAlias
; Arrivals and nights are reported to Service; Service decides what they count for.
EA_Service Property Service Auto

Event OnInit()
    RegisterForSleep()
EndEvent

Event OnPlayerLoadGame()
    RegisterForSleep()
EndEvent

Event OnSleepStop(Bool abInterrupted)
    Service.OnWake()
EndEvent

Event OnLocationChange(Location akOldLoc, Location akNewLoc)
    Service.RecordVisit(akNewLoc)
EndEvent
