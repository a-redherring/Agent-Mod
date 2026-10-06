Scriptname EA_Dispatch extends Quest

EA_Core Property Core Auto
ObjectReference Property Archive Auto
Int[] transactionIDs
Int[] subjects
Int[] outcomes
Int[] states
Float[] arrivalDays
Book[] replies
EA_Module[] receivers
Book[] retainedDocuments
Bool[] documentIssued
Int documentCount = 0
Int count = 0
Bool initialized = False

Function Initialize()
    If initialized
        Return
    EndIf
    transactionIDs = new Int[128]
    subjects = new Int[128]
    outcomes = new Int[128]
    states = new Int[128]
    arrivalDays = new Float[128]
    replies = new Book[128]
    receivers = new EA_Module[128]
    retainedDocuments = new Book[128]
    documentIssued = new Bool[128]
    initialized = True
EndFunction

Bool Function HasSpace()
    Initialize()
    Return count < 128 && Archive != None
EndFunction

Int Function FindTransaction(Int transactionID)
    Int i = 0
    While i < count
        If transactionIDs[i] == transactionID
            Return i
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Bool Function Queue(Int transactionID, Int subjectID, Int outcome, Book outgoing, Book response, EA_Module receiver, Float transitDays = 1.0)
    Initialize()
    If !Core.IsInService() || !HasSpace() || transactionID <= 0 || FindTransaction(transactionID) >= 0
        Return False
    EndIf
    If outgoing == None || response == None || receiver == None || transitDays < 0.25
        Return False
    EndIf
    Int needed = 0
    If FindDocument(outgoing) < 0
        needed += 1
    EndIf
    If response != outgoing && FindDocument(response) < 0
        needed += 1
    EndIf
    If documentCount + needed > 128
        Return False
    EndIf
    ; Reserve recovery slots before committing, but do not release the reply early.
    ReserveDocument(outgoing)
    ReserveDocument(response)
    ; No instant dispatch: the minimum transit is six game hours.
    transactionIDs[count] = transactionID
    subjects[count] = subjectID
    outcomes[count] = outcome
    arrivalDays[count] = Utility.GetCurrentGameTime() + transitDays
    replies[count] = response
    receivers[count] = receiver
    states[count] = 1
    count += 1
    ArchiveDocument(outgoing)
    ScheduleNext()
    Core.Trace("Dispatch filed: " + transactionID)
    Return True
EndFunction

Bool Function Send(Int transactionID, Int subjectID, Book letter, EA_Module receiver)
    ; A letter that answers no report. It is in the case at once; collecting it runs the receiver once.
    Initialize()
    If !Core.IsInService() || !HasSpace() || transactionID <= 0 || FindTransaction(transactionID) >= 0
        Return False
    ElseIf letter == None || receiver == None || ReserveDocument(letter) < 0
        Return False
    EndIf
    transactionIDs[count] = transactionID
    subjects[count] = subjectID
    outcomes[count] = 0
    arrivalDays[count] = Utility.GetCurrentGameTime()
    replies[count] = letter
    receivers[count] = receiver
    states[count] = 1
    count += 1
    Debug.Notification("Something has been left in the dispatch case.")
    Core.Trace("Dispatch letter: " + transactionID)
    Return True
EndFunction

Int Function CountResponses(Bool ready)
    Int result = 0
    Int i = 0
    Float nowDay = Utility.GetCurrentGameTime()
    While i < count
        If states[i] == 1 && (arrivalDays[i] <= nowDay) == ready
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Int Function CollectResponses()
    Initialize()
    If !Core.IsInService() || Archive == None
        Return 0
    EndIf
    Int collected = 0
    Int i = 0
    Float nowDay = Utility.GetCurrentGameTime()
    While i < count
        If states[i] == 1 && arrivalDays[i] <= nowDay
            ; Claim before inventory or callback calls; repeat collection cannot pay twice.
            states[i] = 2
            Game.GetPlayer().AddItem(replies[i], 1, True)
            ArchiveDocument(replies[i])
            receivers[i].ReceiveResponse(transactionIDs[i], subjects[i], outcomes[i])
            states[i] = 3
            collected += 1
        EndIf
        i += 1
    EndWhile
    ScheduleNext()
    Return collected
EndFunction

Bool Function IsDelivering(Int transactionID, Int subjectID, Int outcome, EA_Module receiver)
    ; Receiver validation: callbacks must correspond to the response being collected.
    Int i = FindTransaction(transactionID)
    If transactionID <= 0 || i < 0 || !Core.IsInService()
        Return False
    EndIf
    Return states[i] == 2 && subjects[i] == subjectID && outcomes[i] == outcome && receivers[i] == receiver && arrivalDays[i] <= Utility.GetCurrentGameTime()
EndFunction

Function ScheduleNext()
    UnregisterForUpdateGameTime()
    Float nextDay = 0.0
    Float nowDay = Utility.GetCurrentGameTime()
    Int i = 0
    While i < count
        If states[i] == 1 && arrivalDays[i] > nowDay
            If nextDay == 0.0 || arrivalDays[i] < nextDay
                nextDay = arrivalDays[i]
            EndIf
        EndIf
        i += 1
    EndWhile
    If nextDay > nowDay
        Float hours = (nextDay - nowDay) * 24.0
        If hours < 0.1
            hours = 0.1
        EndIf
        RegisterForSingleUpdateGameTime(hours)
    EndIf
EndFunction

Event OnUpdateGameTime()
    ; A one-shot notification, never a polling loop or remote delivery.
    Int i = 0
    Bool ready = False
    While i < count && !ready
        ready = states[i] == 1 && arrivalDays[i] <= Utility.GetCurrentGameTime()
        i += 1
    EndWhile
    If ready
        Debug.Notification("Correspondence may be collected at the secure dispatch box.")
    EndIf
    ScheduleNext()
EndEvent

Function RecoverDocument(Book document)
    Int index = FindDocument(document)
    If document != None && Archive != None && index >= 0 && documentIssued[index]
        If Archive.GetItemCount(document) == 0
            Archive.AddItem(document, 1, True)
        EndIf
        If Game.GetPlayer().GetItemCount(document) == 0
            Game.GetPlayer().AddItem(document, 1, True)
        EndIf
    EndIf
EndFunction

Int Function FindDocument(Book document)
    Int i = 0
    While i < documentCount
        If retainedDocuments[i] == document
            Return i
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Int Function ReserveDocument(Book document)
    Initialize()
    Int index = FindDocument(document)
    If index >= 0
        Return index
    EndIf
    If document == None || documentCount >= 128
        Return -1
    EndIf
    index = documentCount
    retainedDocuments[index] = document
    documentCount += 1
    Return index
EndFunction

Bool Function ArchiveDocument(Book document)
    If document == None || Archive == None
        Return False
    EndIf
    Int index = ReserveDocument(document)
    If index < 0
        Return False
    EndIf
    documentIssued[index] = True
    Archive.AddItem(document, 1, True)
    Return True
EndFunction

Function RecoverFiledCopies()
    Int i = 0
    While i < documentCount
        RecoverDocument(retainedDocuments[i])
        i += 1
    EndWhile
EndFunction

Bool Function DebugRecoverPending(Int transactionID)
    ; Development-only, requires explicit Core.DebugEnabled. No player menu entry.
    If !Core.DebugEnabled
        Return False
    EndIf
    Int i = FindTransaction(transactionID)
    If i < 0 || states[i] != 2
        Return False
    EndIf
    ; Receivers independently guard their transaction IDs / final settlement state.
    receivers[i].ReceiveResponse(transactionIDs[i], subjects[i], outcomes[i])
    ArchiveDocument(replies[i])
    RecoverDocument(replies[i])
    states[i] = 3
    Core.Trace("Recovered interrupted callback: " + transactionID)
    Return True
EndFunction
