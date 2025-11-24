from enum import IntEnum
from dataclasses import dataclass

class LedPacketHead(IntEnum):
    COMMAND = 0x33
    REQUEST = 0xaa

class LedPacketCmd(IntEnum):
    POWER      = 0x01
    BRIGHTNESS = 0x04
    COLOR      = 0x05
    SEGMENT    = 0xa5

class LedColorType(IntEnum):
    SEGMENTS    = 0x15
    SINGLE      = 0x02
    LEGACY      = 0x0D
    EFFECT      = 0x04  # Scene/Effect mode

class LedEffect(IntEnum):
    """Govee light effect codes."""
    SUNRISE     = 0x00
    SUNSET      = 0x01
    MOVIE       = 0x02
    DATING      = 0x03
    ROMANTIC    = 0x04
    BLINKING    = 0x05
    CANDLELIGHT = 0x06
    SNOWFLAKE   = 0x07
    ENERGETIC   = 0x08
    SPECTRUM    = 0x09
    RAINBOW     = 0x0a
    BREATHING   = 0x0b
    CROSSING    = 0x0c

# Effect names for Home Assistant
EFFECT_LIST = [
    "Sunrise",
    "Sunset",
    "Movie",
    "Dating",
    "Romantic",
    "Blinking",
    "Candlelight",
    "Snowflake",
    "Energetic",
    "Spectrum",
    "Rainbow",
    "Breathing",
    "Crossing",
]

def effect_name_to_code(name: str) -> int | None:
    """Convert effect name to code."""
    try:
        index = EFFECT_LIST.index(name)
        return index
    except ValueError:
        return None

def effect_code_to_name(code: int) -> str | None:
    """Convert effect code to name."""
    if 0 <= code < len(EFFECT_LIST):
        return EFFECT_LIST[code]
    return None

@dataclass
class LedPacket:
    #request data or perform a change
    head: LedPacketHead
    #data to request or command to perform
    cmd: LedPacketCmd
    #actual data to transmit
    payload: bytes | list = b''

class GoveeUtils:
    @staticmethod
    async def generateChecksum(frame: bytes):
        """ returns checksum by XORing all data bytes """
        checksum = 0
        for b in frame:
            checksum ^= b
        #pad response to 8 bits
        return bytes([checksum & 0xFF])

    @staticmethod
    async def generateFrame(packet: LedPacket):
        """ returns transmittable frame bytes """
        #pad cmd to 8 bits
        cmd = packet.cmd & 0xFF
        #combine segments
        frame = bytes([packet.head, cmd]) + bytes(packet.payload)
        #pad frame data to 19 bytes (plus checksum)
        frame += bytes([0] * (19 - len(frame)))
        #add checksum to end
        frame += await GoveeUtils.generateChecksum(frame)
        return frame

    @staticmethod
    async def verifyChecksum(frame: bytes):
        checksum_received = frame[-1].to_bytes(1, 'big')
        checksum_calculated = await GoveeUtils.generateChecksum(frame[:-1])
        return checksum_received == checksum_calculated
