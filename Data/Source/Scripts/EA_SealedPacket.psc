Scriptname EA_SealedPacket extends ObjectReference
; Breaking the seal issues the packet's contents once.
EA_Opening Property Opening Auto

Event OnRead()
    Opening.OpenPacket()
EndEvent
