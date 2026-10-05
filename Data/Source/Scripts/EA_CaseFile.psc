Scriptname EA_CaseFile extends ObjectReference
; Reading the issued case papers is the fact a judgement report rests on.
EA_Core Property Core Auto
Int Property AssignmentID Auto

Event OnRead()
    Core.RecordFact(AssignmentID, 1)
EndEvent
