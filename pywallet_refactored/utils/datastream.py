"""
BCDataStream implementation for parsing binary data from wallet.dat.
"""
import struct
import mmap
from typing import Any, Union, Optional

class BCDataStream:
    """
    Parse binary data from wallet.dat.
    """
    def __init__(self):
        self.input = None
        self.read_cursor = 0

    def clear(self):
        """Clear the stream."""
        self.input = None
        self.read_cursor = 0

    def write(self, data: bytes):
        """Write data to the stream."""
        if self.input is None:
            self.input = data
        else:
            self.input += data

    def map_file(self, file, start: int):
        """Map a file to the stream."""
        self.input = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        self.read_cursor = start

    def seek_file(self, position: int):
        """Seek to a position in the file."""
        self.read_cursor = position

    def close_file(self):
        """Close the file."""
        self.input.close()

    def read_string(self) -> bytes:
        """Read a string from the stream."""
        if self.input is None:
            return b""
        length = self.read_compact_size()
        return self.read_bytes(length)

    def read_bytes(self, length: int) -> bytes:
        """Read bytes from the stream."""
        try:
            result = self.input[self.read_cursor:self.read_cursor+length]
            self.read_cursor += length
            return result
        except IndexError:
            raise IndexError("read_bytes: IndexError")

    def read_boolean(self) -> bool:
        """Read a boolean from the stream."""
        return self.read_bytes(1)[0] != 0

    def read_int16(self) -> int:
        """Read a 16-bit integer from the stream."""
        return struct.unpack("<h", self.read_bytes(2))[0]

    def read_uint16(self) -> int:
        """Read a 16-bit unsigned integer from the stream."""
        return struct.unpack("<H", self.read_bytes(2))[0]

    def read_int32(self) -> int:
        """Read a 32-bit integer from the stream."""
        return struct.unpack("<i", self.read_bytes(4))[0]

    def read_uint32(self) -> int:
        """Read a 32-bit unsigned integer from the stream."""
        return struct.unpack("<I", self.read_bytes(4))[0]

    def read_int64(self) -> int:
        """Read a 64-bit integer from the stream."""
        return struct.unpack("<q", self.read_bytes(8))[0]

    def read_uint64(self) -> int:
        """Read a 64-bit unsigned integer from the stream."""
        return struct.unpack("<Q", self.read_bytes(8))[0]

    def read_compact_size(self) -> int:
        """Read a compact size from the stream."""
        size = self.input[self.read_cursor]
        self.read_cursor += 1
        if size == 253:
            size = self.read_uint16()
        elif size == 254:
            size = self.read_uint32()
        elif size == 255:
            size = self.read_uint64()
        return size
