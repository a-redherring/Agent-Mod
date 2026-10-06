Scriptname EA_Module extends Quest
; Common callback type prevents a dependency from Dispatch to its clients.
Function ReceiveResponse(Int transactionID, Int subjectID, Int outcome)
EndFunction

Bool Function FileCoverReport()
    ; Overridden by a start module while its cover report is outstanding.
    Return False
EndFunction
