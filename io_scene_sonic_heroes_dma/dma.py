from os import SEEK_SET, SEEK_CUR, SEEK_END
import struct
from dataclasses import dataclass

DMA_CHUNK_ID = 0x1e
DMA_ANIM_VERSION = 0x100


def read_float32(fd, num=1, en='<'):
    res = struct.unpack('%s%df' % (en, num), fd.read(4 * num))
    return res if num > 1 else res[0]


def read_uint32(fd, num=1, en='<'):
    res = struct.unpack('%s%dI' % (en, num), fd.read(4 * num))
    return res if num > 1 else res[0]


def write_uint32(fd, vals, en='<'):
    data = vals if hasattr(vals, '__len__') else (vals, )
    data = struct.pack('%s%dI' % (en, len(data)), *data)
    fd.write(data)


def write_float32(fd, vals, en='<'):
    data = vals if hasattr(vals, '__len__') else (vals, )
    data = struct.pack('%s%df' % (en, len(data)), *data)
    fd.write(data)


def unpack_rw_lib_id(version):
    v = (version >> 14 & 0x3ff00) + 0x30000 | (version >> 16 & 0x3f)
    bin_ver = v & 0x3f
    min_rev = (v >> 8) & 0xf
    maj_rev = (v >> 12) & 0xf
    rw_ver = (v >> 16) & 0x7
    return rw_ver, maj_rev, min_rev, bin_ver


def pack_rw_lib_id(rw_ver, maj_rev, min_rev, bin_ver):
    ver = ((rw_ver & 0x7) << 16) | ((maj_rev & 0xf) << 12) | ((min_rev & 0xf) << 8) | (bin_ver & 0x3f)
    ver -= 0x30000
    b = ver & 0xff
    n = (ver >> 8) & 0xf
    j = (ver >> 12) & 0xf
    v = (ver >> 16) & 0xf
    return 0xffff | (b << 16) | (n << 22) | (j << 26) | (v << 30)


@dataclass
class DMAFrame:
    start_val: float
    end_val: float
    duration: float
    recip_duration: float
    next_frame: int

    @classmethod
    def read(cls, fd):
        return cls(*read_float32(fd, 4), read_uint32(fd))

    def write(self, fd):
        write_float32(fd, (self.start_val, self.end_val, self.duration, self.recip_duration))
        write_uint32(fd, self.next_frame)

    @staticmethod
    def get_size():
        return 20


@dataclass
class DMATarget:
    frames: list

    @classmethod
    def read(cls, fd):
        frames_num = read_uint32(fd)
        return cls([DMAFrame.read(fd) for _ in range(frames_num)])

    def write(self, fd):
        write_uint32(fd, len(self.frames))
        for f in self.frames:
            f.write(fd)

    def get_size(self):
        return 4 + DMAFrame.get_size() * len(self.frames)


@dataclass
class DMAction:
    anim_version: int
    anim_flags: int
    targets: list

    @classmethod
    def read(cls, fd):
        read_uint32(fd) # always 1?
        size, version = read_uint32(fd, 2)

        anim_version, anim_flags, targets_num, frames_num = read_uint32(fd, 4)
        return cls(anim_version, anim_flags, [DMATarget.read(fd) for _ in range(targets_num)])

    def write(self, fd, version):
        write_uint32(fd, (1, self.get_size() - 12, version))
        write_uint32(fd, (self.anim_version, self.anim_flags, len(self.targets), sum(len(t.frames) for t in self.targets)))
        for t in self.targets:
            t.write(fd)

    def get_size(self):
        return 12 + 16 + sum((t.get_size() for t in self.targets))


@dataclass
class DMAChunk:
    chunk_id: int
    version: int
    action: DMAction


@dataclass
class DMA:
    chunks: []

    @classmethod
    def read(cls, fd):
        fd.seek(0, SEEK_END)
        file_size = fd.tell()
        fd.seek(0, SEEK_SET)

        chunks = []

        while fd.tell() < file_size:
            chunk_id, chunk_size, chunk_version = read_uint32(fd, 3)
            if chunk_id == DMA_CHUNK_ID:
                dma_chunk = DMAChunk(chunk_id, chunk_version, DMAction.read(fd))
                chunks.append(dma_chunk)
            else:
                fd.seek(chunk_size, SEEK_CUR)

        return cls(chunks)

    @classmethod
    def load(cls, filepath):
        with open(filepath, 'rb') as fd:
            return cls.read(fd)

    def write(self, fd):
        for dma_chunk in self.chunks:
            write_uint32(fd, (dma_chunk.chunk_id, dma_chunk.action.get_size(), dma_chunk.version)) # fix get_size()
            dma_chunk.action.write(fd, dma_chunk.version)

    def save(self, filepath):
        with open(filepath, 'wb') as fd:
            return self.write(fd)
