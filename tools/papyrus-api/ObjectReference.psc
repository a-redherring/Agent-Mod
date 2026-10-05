Scriptname ObjectReference extends Form Hidden
Function AddItem(Form akItemToAdd, Int aiCount = 1, Bool abSilent = False) Native
Function RemoveItem(Form akItemToRemove, Int aiCount = 1, Bool abSilent = False, ObjectReference akOtherContainer = None) Native
Int Function GetItemCount(Form akItem) Native
ObjectReference Function PlaceAtMe(Form akFormToPlace, Int aiCount = 1, Bool abForcePersist = False, Bool abInitiallyDisabled = False) Native
Function MoveTo(ObjectReference akTarget, Float afXOffset = 0.0, Float afYOffset = 0.0, Float afZOffset = 0.0, Bool abMatchRotation = True) Native
Event OnActivate(ObjectReference akActionRef)
EndEvent
Event OnRead()
EndEvent
