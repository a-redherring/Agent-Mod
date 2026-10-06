"""Independent, read-only TES4/GRUP/VMAD inspection for this generated plugin subset."""
import io
import struct
from dataclasses import dataclass


@dataclass
class Record:
    kind: str
    flags: int
    form_id: int
    version: int
    fields: list

    def field(self, kind):
        return next((value for name, value in self.fields if name == kind), None)

    @property
    def editor_id(self):
        raw = self.field("EDID")
        return raw.rstrip(b"\0").decode() if raw else None


def records(data):
    pos = 0
    while pos < len(data):
        assert pos + 24 <= len(data), "Truncated header"
        kind = data[pos:pos + 4].decode("ascii")
        size = struct.unpack_from("<I", data, pos + 4)[0]
        if kind == "GRUP":
            assert size >= 24 and pos + size <= len(data), "Invalid group size"
            yield from records(data[pos + 24:pos + size])
            pos += size
            continue
        flags, form_id = struct.unpack_from("<II", data, pos + 8)
        version = struct.unpack_from("<H", data, pos + 20)[0]
        assert not flags & 0x40000, "Unexpected compressed record"
        end = pos + 24 + size
        assert end <= len(data), "Truncated record"
        body = data[pos + 24:end]
        fields = []
        subpos = 0
        while subpos < len(body):
            name, length = struct.unpack_from("<4sH", body, subpos)
            subpos += 6
            assert subpos + length <= len(body), "Truncated subrecord"
            fields.append((name.decode(), body[subpos:subpos + length]))
            subpos += length
        yield Record(kind, flags, form_id, version, fields)
        pos = end


def scripts(data):
    if data is None:
        return []
    stream = io.BytesIO(data)

    def number(fmt):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, stream.read(size))[0]

    def string():
        return stream.read(number("<H")).decode()

    def obj():
        unused = number("<H")
        alias = number("<h")
        form_id = number("<I")
        assert unused == 0 and alias == -1, "Unexpected reference alias binding"
        return form_id

    assert number("<H") == 5, "Unexpected VMAD version"
    assert number("<H") == 2, "Unexpected object format"
    result = []
    for _ in range(number("<H")):
        name = string()
        assert number("<B") == 0, "Unexpected script flags"
        properties = {}
        for _ in range(number("<H")):
            prop = string()
            assert prop not in properties, "Duplicate VMAD property"
            kind = number("<B")
            assert number("<B") == 1, "Property must be marked edited"
            if kind == 1:
                value = obj()
            elif kind == 3:
                value = number("<i")
            elif kind == 2:
                value = string()
            elif kind == 11:
                value = [obj() for _ in range(number("<I"))]
            elif kind == 12:
                value = [string() for _ in range(number("<I"))]
            elif kind == 13:
                value = [number("<i") for _ in range(number("<I"))]
            else:
                raise AssertionError("Unexpected VMAD property type: " + str(kind))
            properties[prop] = value
        result.append((name, properties))
    return result
