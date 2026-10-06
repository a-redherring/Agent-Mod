Scriptname EA_ServicePlayer extends ReferenceAlias
; Arrivals at named places are reported to Service; Service decides whether they count.
EA_Service Property Service Auto

Event OnLocationChange(Location akOldLoc, Location akNewLoc)
    Service.RecordVisit(akNewLoc)
EndEvent
