"""ActionScript 2 bytecode opcodes."""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.action.define_function2_data import DefineFunction2Data
from prespyc.parser.structure.action.define_function_data import DefineFunctionData
from prespyc.parser.structure.action.get_url2_data import GetURL2Data
from prespyc.parser.structure.action.get_url_data import GetURLData
from prespyc.parser.structure.action.goto_frame2_data import GotoFrame2Data
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.action.wait_for_frame_data import WaitForFrameData

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


class Opcode(IntEnum):
    """
    All ActionScript 2 bytecodes. The value is the opcode of the bytecode.

    Beware: `Opcode.NULL` is `0`, so it is falsy. Always test membership with `is None`.
    """

    NULL = 0x00

    # SWF 3
    ACTION_GOTO_FRAME = 0x81
    ACTION_GET_URL = 0x83
    ACTION_NEXT_FRAME = 0x04
    ACTION_PREVIOUS_FRAME = 0x05
    ACTION_PLAY = 0x06
    ACTION_STOP = 0x07
    ACTION_TOGGLE_QUALITY = 0x08
    ACTION_STOP_SOUNDS = 0x09
    ACTION_WAIT_FOR_FRAME = 0x8A
    ACTION_SET_TARGET = 0x8B
    ACTION_GO_TO_LABEL = 0x8C

    # SWF 4
    ACTION_PUSH = 0x96  # Stack operations
    ACTION_POP = 0x17
    ACTION_ADD = 0x0A  # Arithmetic operators
    ACTION_SUBTRACT = 0x0B
    ACTION_MULTIPLY = 0x0C
    ACTION_DIVIDE = 0x0D
    ACTION_EQUALS = 0x0E  # Numerical comparison
    ACTION_LESS = 0x0F
    ACTION_AND = 0x10  # Logical operators
    ACTION_OR = 0x11
    ACTION_NOT = 0x12
    ACTION_STRING_EQUALS = 0x13  # String manipulation
    ACTION_STRING_LENGTH = 0x14
    ACTION_STRING_ADD = 0x21
    ACTION_STRING_EXTRACT = 0x15
    ACTION_STRING_LESS = 0x29
    ACTION_MB_STRING_LENGTH = 0x31
    ACTION_MB_STRING_EXTRACT = 0x35
    ACTION_TO_INTEGER = 0x18  # Type conversion
    ACTION_CHAR_TO_ASCII = 0x32
    ACTION_ASCII_TO_CHAR = 0x33
    ACTION_MB_CHAR_TO_ASCII = 0x36
    ACTION_MB_ASCII_TO_CHAR = 0x37
    ACTION_JUMP = 0x99  # Control flow
    ACTION_IF = 0x9D
    ACTION_CALL = 0x9E
    ACTION_GET_VARIABLE = 0x1C  # Variables
    ACTION_SET_VARIABLE = 0x1D
    ACTION_GET_URL2 = 0x9A  # Movie control
    ACTION_GOTO_FRAME2 = 0x9F
    ACTION_SET_TARGET2 = 0x20
    ACTION_GET_PROPERTY = 0x22
    ACTION_SET_PROPERTY = 0x23
    ACTION_CLONE_SPRITE = 0x24
    ACTION_REMOTE_SPRITE = 0x25
    ACTION_START_DRAG = 0x27
    ACTION_END_DRAG = 0x28
    ACTION_WAIT_FOR_FRAME2 = 0x8D
    ACTION_TRACE = 0x26  # Utilities
    ACTION_GET_TIME = 0x34
    ACTION_RANDOM_NUMBER = 0x30

    # SWF 5
    ACTION_CALL_FUNCTION = 0x3D  # ScriptObject actions
    ACTION_CALL_METHOD = 0x52
    ACTION_CONSTANT_POOL = 0x88
    ACTION_DEFINE_FUNCTION = 0x9B
    ACTION_DEFINE_LOCAL = 0x3C
    ACTION_DEFINE_LOCAL2 = 0x41
    ACTION_DELETE = 0x3A
    ACTION_DELETE2 = 0x3B
    ACTION_ENUMERATE = 0x46
    ACTION_EQUALS2 = 0x49
    ACTION_GET_MEMBER = 0x4E
    ACTION_INIT_ARRAY = 0x42
    ACTION_INIT_OBJECT = 0x43
    ACTION_NEW_METHOD = 0x53
    ACTION_NEW_OBJECT = 0x40
    ACTION_SET_MEMBER = 0x4F
    ACTION_TARGET_PATH = 0x45
    ACTION_WITH = 0x94
    ACTION_TO_NUMBER = 0x4A  # Type actions
    ACTION_TO_STRING = 0x4B
    ACTION_TYPE_OF = 0x44
    ACTION_ADD2 = 0x47  # Math actions
    ACTION_LESS2 = 0x48
    ACTION_MODULE = 0x3F
    ACTION_BIT_AND = 0x60  # Stack operator actions
    ACTION_BIT_LSHIFT = 0x63
    ACTION_BIT_OR = 0x61
    ACTION_BIT_RSHIFT = 0x64
    ACTION_BIT_URSHIFT = 0x65
    ACTION_BIT_XOR = 0x62
    ACTION_DECREMENT = 0x51
    ACTION_INCREMENT = 0x50
    ACTION_PUSH_DUPLICATE = 0x4C
    ACTION_RETURN = 0x3E
    ACTION_STACK_SWAP = 0x4D
    ACTION_STORE_REGISTER = 0x87

    # SWF 6
    DO_INIT_ACTION = 0x59
    ACTION_INSTANCE_OF = 0x54
    ACTION_ENUMERATE2 = 0x55
    ACTION_STRICT_EQUALS = 0x66
    ACTION_GREATER = 0x67
    ACTION_STRING_GREATER = 0x68

    # SWF 7
    ACTION_DEFINE_FUNCTION2 = 0x8E
    ACTION_EXTENDS = 0x69
    ACTION_CAST_OP = 0x2B
    ACTION_IMPLEMENTS_OP = 0x2C
    ACTION_TRY = 0x8F
    ACTION_THROW = 0x2A

    # SWF 9
    DO_ABC = 0x82
    # SWF 10

    @classmethod
    def try_from(cls, value: int) -> Opcode | None:
        """Member with this opcode value, or `None` when the value is not a known opcode."""
        try:
            return cls(value)
        except ValueError:
            return None

    def read_data(self, reader: Reader, length: int) -> Any:
        """Read the payload data of the action related to the opcode. `length` is the action length."""
        match self:
            case Opcode.ACTION_GOTO_FRAME:
                return reader.read_ui16()
            case Opcode.ACTION_GET_URL:
                return GetURLData.read(reader)
            case Opcode.ACTION_STORE_REGISTER:
                return reader.read_ui8()
            case Opcode.ACTION_CONSTANT_POOL:
                return self._read_constant_pool(reader)
            case Opcode.ACTION_WAIT_FOR_FRAME:
                return WaitForFrameData.read(reader)
            case Opcode.ACTION_SET_TARGET:
                return reader.read_null_terminated_string()
            case Opcode.ACTION_GO_TO_LABEL:
                return reader.read_null_terminated_string()
            case Opcode.ACTION_WAIT_FOR_FRAME2:
                return reader.read_ui8()
            case Opcode.ACTION_DEFINE_FUNCTION2:
                return DefineFunction2Data.read(reader)
            case Opcode.ACTION_WITH:
                return reader.read_bytes(reader.read_ui16())
            case Opcode.ACTION_PUSH:
                return Value.read_collection(reader, length)
            case Opcode.ACTION_JUMP | Opcode.ACTION_IF:
                return reader.read_si16()
            case Opcode.ACTION_GET_URL2:
                return GetURL2Data.read(reader)
            case Opcode.ACTION_DEFINE_FUNCTION:
                return DefineFunctionData.read(reader)
            case Opcode.ACTION_GOTO_FRAME2:
                return GotoFrame2Data.read(reader)
            case _:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(
                        f"Unexpected data for opcode {self.name}, actionLength={length}", reader.offset
                    )

                return reader.read_bytes(length)

    def _read_constant_pool(self, reader: Reader) -> list[bytes]:
        data = []
        count = reader.read_ui16()

        for _ in range(count):
            data.append(reader.read_null_terminated_string())

        return data
