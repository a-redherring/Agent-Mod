Scriptname EA_Core extends Quest
; Persistent shared state. No SKSE, external mod events, or vanilla quest writes.
; Assignment states: 1 active, 2 overdue, 3 filed, 4 complete, 5 withdrawn, 6 failed.
; Classes: 1 major, 2 intelligence, 3 duty. Authority: 1 standing, 2 prior, 3 emergency.

Bool Property DebugEnabled = False Auto
Bool initialized = False
Bool serviceActive = False
Bool coverEstablished = False
Bool coverCompromised = False
Bool fieldPapersRead = False
Int professionalTrust = 50
Int nextTransaction = 1
Int[] assignmentIDs
Int[] assignmentClasses
Int[] assignmentStates
Int[] assignmentFacts
Bool[] assignmentMissedDeadline
Float[] assignmentDue
Float[] deadlineFrozenAt
Int assignmentCount = 0
Int[] authorityOperations
Int[] authorityCategories
Int[] authorityModes
Float[] authorityExpiry
Bool[] emergencyReview
Int authorityCount = 0
Float suspensionStarted = -1.0
Int suspensionDepth = 0

Function Initialize()
    If initialized
        Return
    EndIf
    assignmentIDs = new Int[64]
    assignmentClasses = new Int[64]
    assignmentStates = new Int[64]
    assignmentFacts = new Int[64]
    assignmentMissedDeadline = new Bool[64]
    assignmentDue = new Float[64]
    deadlineFrozenAt = new Float[64]
    authorityOperations = new Int[64]
    authorityCategories = new Int[64]
    authorityModes = new Int[64]
    authorityExpiry = new Float[64]
    emergencyReview = new Bool[64]
    initialized = True
EndFunction

Bool Function Commission()
    Initialize()
    If serviceActive
        Return False
    EndIf
    serviceActive = True
    Trace("Commission activated")
    Return True
EndFunction

Bool Function IsInService()
    Return serviceActive
EndFunction

Function SetCoverStatus(Bool established, Bool compromised)
    ; Reserved for validated start / investigation hooks, not a player menu.
    If serviceActive
        coverEstablished = established
        coverCompromised = compromised
    EndIf
EndFunction

Bool Function HasEstablishedCover()
    Return coverEstablished
EndFunction

Bool Function HasCompromisedCover()
    Return coverCompromised
EndFunction

Function RecordFieldPapersRead()
    If serviceActive
        fieldPapersRead = True
        RecordFact(1001, 1)
    EndIf
EndFunction

Bool Function HasReadFieldPapers()
    Return fieldPapersRead
EndFunction

Int Function NextTransactionID()
    Initialize()
    Int result = nextTransaction
    nextTransaction += 1
    Return result
EndFunction

Int Function FindAssignment(Int assignmentID)
    Initialize()
    Int i = 0
    While i < assignmentCount
        If assignmentIDs[i] == assignmentID
            Return i
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Int Function CountWorkload(Int assignmentClass)
    Int result = 0
    Int i = 0
    While i < assignmentCount
        If assignmentClasses[i] == assignmentClass && assignmentStates[i] >= 1 && assignmentStates[i] <= 3
            result += 1
        EndIf
        i += 1
    EndWhile
    Return result
EndFunction

Bool Function RegisterAssignment(Int assignmentID, Int assignmentClass, Float dueDay)
    Initialize()
    If !serviceActive || assignmentID <= 0 || dueDay < 0.0 || assignmentCount >= 64 || FindAssignment(assignmentID) >= 0
        Return False
    EndIf
    Int capacity = 0
    If assignmentClass == 1
        capacity = 1
    ElseIf assignmentClass == 2
        capacity = 3
    ElseIf assignmentClass == 3
        capacity = 6
    EndIf
    If capacity == 0 || CountWorkload(assignmentClass) >= capacity
        Return False
    EndIf
    assignmentIDs[assignmentCount] = assignmentID
    assignmentClasses[assignmentCount] = assignmentClass
    assignmentStates[assignmentCount] = 1
    assignmentDue[assignmentCount] = dueDay
    If suspensionDepth > 0
        deadlineFrozenAt[assignmentCount] = Utility.GetCurrentGameTime()
    EndIf
    assignmentCount += 1
    Trace("Assignment registered: " + assignmentID)
    Return True
EndFunction

Int Function GetAssignmentState(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    If index < 0
        Return 0
    EndIf
    Return assignmentStates[index]
EndFunction

Bool Function IsOpen(Int assignmentID)
    Int status = GetAssignmentState(assignmentID)
    Return status == 1 || status == 2
EndFunction

Float Function GetDaysRemaining(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    If index < 0 || !IsOpen(assignmentID)
        Return 0.0
    EndIf
    Float nowDay = Utility.GetCurrentGameTime()
    If suspensionDepth > 0
        nowDay = deadlineFrozenAt[index]
    EndIf
    Return assignmentDue[index] - nowDay
EndFunction

Bool Function HasMissedDeadline(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    Return index >= 0 && assignmentMissedDeadline[index]
EndFunction

Bool Function RecordFact(Int assignmentID, Int fact)
    ; This prototype uses one fact flag per assignment, set only by authored hooks.
    Int index = FindAssignment(assignmentID)
    If index < 0 || !IsOpen(assignmentID) || fact != 1
        Return False
    EndIf
    assignmentFacts[index] = 1
    Return True
EndFunction

Bool Function HasFact(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    Return index >= 0 && assignmentFacts[index] == 1
EndFunction

Bool Function FileAssignment(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    If index < 0 || !IsOpen(assignmentID) || !HasFact(assignmentID)
        Return False
    EndIf
    assignmentStates[index] = 3
    Return True
EndFunction

Bool Function CompleteAssignment(Int assignmentID)
    Int index = FindAssignment(assignmentID)
    If index < 0 || assignmentStates[index] != 3
        Return False
    EndIf
    assignmentStates[index] = 4
    AdjustTrust(1)
    Trace("Assignment completed: " + assignmentID)
    Return True
EndFunction

Function RefreshDeadlines(Float nowDay)
    If suspensionStarted >= 0.0
        Return
    EndIf
    Int i = 0
    While i < assignmentCount
        If assignmentStates[i] == 1 && assignmentDue[i] > 0.0 && nowDay > assignmentDue[i]
            assignmentStates[i] = 2
            assignmentMissedDeadline[i] = True
            AdjustTrust(-1)
            Trace("Assignment overdue: " + assignmentIDs[i])
        EndIf
        i += 1
    EndWhile
EndFunction

Bool Function ExtendAssignment(Int assignmentID, Float days)
    Int index = FindAssignment(assignmentID)
    If index < 0 || days <= 0.0 || !IsOpen(assignmentID) || assignmentDue[index] <= 0.0
        Return False
    EndIf
    Float nowDay = Utility.GetCurrentGameTime()
    If suspensionDepth > 0
        nowDay = deadlineFrozenAt[index]
    EndIf
    If assignmentDue[index] < nowDay
        assignmentDue[index] = nowDay
    EndIf
    assignmentDue[index] = assignmentDue[index] + days
    assignmentStates[index] = 1
    Return True
EndFunction

Function SuspendDeadlines()
    ; Balanced nested brackets permit two unavoidable scenes to overlap.
    If suspensionDepth == 0
        Float nowDay = Utility.GetCurrentGameTime()
        RefreshDeadlines(nowDay)
        suspensionStarted = nowDay
        Int i = 0
        While i < assignmentCount
            deadlineFrozenAt[i] = nowDay
            i += 1
        EndWhile
    EndIf
    suspensionDepth += 1
EndFunction

Function ResumeDeadlines()
    If suspensionDepth == 0
        Return
    EndIf
    suspensionDepth -= 1
    If suspensionDepth > 0
        Return
    EndIf
    Float nowDay = Utility.GetCurrentGameTime()
    Int i = 0
    While i < assignmentCount
        If (assignmentStates[i] == 1 || assignmentStates[i] == 2) && assignmentDue[i] > 0.0
            assignmentDue[i] = assignmentDue[i] + nowDay - deadlineFrozenAt[i]
        EndIf
        i += 1
    EndWhile
    suspensionStarted = -1.0
EndFunction

Int Function FindAuthority(Int operationID, Int category)
    Initialize()
    Int i = 0
    While i < authorityCount
        If authorityOperations[i] == operationID && authorityCategories[i] == category
            Return i
        EndIf
        i += 1
    EndWhile
    Return -1
EndFunction

Bool Function GrantAuthority(Int operationID, Int category, Int mode, Float expiryDay = 0.0)
    ; Call only from authored EA code after an operational brief or decision.
    If !serviceActive || operationID <= 0 || category < 1 || category > 5 || mode < 1 || mode > 3 || expiryDay < 0.0
        Return False
    EndIf
    Int index = FindAuthority(operationID, category)
    If index < 0
        If authorityCount >= 64
            Return False
        EndIf
        index = authorityCount
        authorityCount += 1
    EndIf
    authorityOperations[index] = operationID
    authorityCategories[index] = category
    authorityModes[index] = mode
    authorityExpiry[index] = expiryDay
    Return True
EndFunction

Int Function GetAuthority(Int operationID, Int category)
    Int index = FindAuthority(operationID, category)
    If !serviceActive || index < 0
        Return 0
    EndIf
    If authorityExpiry[index] > 0.0 && Utility.GetCurrentGameTime() > authorityExpiry[index]
        Return 0
    EndIf
    Return authorityModes[index]
EndFunction

Bool Function RecordEmergency(Int operationID, Int category)
    Int index = FindAuthority(operationID, category)
    If index < 0 || GetAuthority(operationID, category) != 3
        Return False
    EndIf
    emergencyReview[index] = True
    Trace("Emergency action awaiting review: " + operationID)
    Return True
EndFunction

Bool Function NeedsEmergencyReview(Int operationID, Int category)
    Int index = FindAuthority(operationID, category)
    Return index >= 0 && emergencyReview[index]
EndFunction

Function ReviewEmergency(Int operationID, Int category, Bool approved)
    Int index = FindAuthority(operationID, category)
    If index < 0 || !emergencyReview[index]
        Return
    EndIf
    emergencyReview[index] = False
    If !approved
        AdjustTrust(-2)
        authorityModes[index] = 0
    EndIf
EndFunction

Function AdjustTrust(Int delta)
    professionalTrust += delta
    If professionalTrust < 0
        professionalTrust = 0
    ElseIf professionalTrust > 100
        professionalTrust = 100
    EndIf
EndFunction

Function Trace(String text)
    If DebugEnabled
        Debug.Trace("[EA] " + text)
    EndIf
EndFunction
