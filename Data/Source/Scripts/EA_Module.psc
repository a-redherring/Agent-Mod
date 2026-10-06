Scriptname EA_Module extends Quest
; Common callback type prevents a dependency from Dispatch to its clients.
Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
EndFunction
