import struct
import zlib
import os
import sys

def read_uint32(f):
    return struct.unpack("<I", f.read(4))[0]

def read_uint16(f):
    return struct.unpack("<H", f.read(2))[0]

def extract_archive(input_file, output_folder):
    with open(input_file, "rb") as f:
        # Get compressed size (ZSIZE)
        f.seek(0, os.SEEK_END)
        zsize = f.tell()
        f.seek(0)

        zsize -= 4

        # Read uncompressed size
        size = read_uint32(f)

        # Read compressed data
        comp_data = f.read(zsize)

        # Decompress (equivalent to clog MEMORY_FILE)
        decompressed = zlib.decompress(comp_data)

    print(f"uncompressed size: {size}, actual len: {len(decompressed)}")

    # Work on MEMORY_FILE (decompressed data)
    mem = decompressed
    offset = 0

    # Read file count
    filenum = struct.unpack_from("<H", mem, offset)[0]
    offset += 2

    print(f"filenum: {filenum}")

    # Jump to 0x50
    offset = 0x50

    os.makedirs(output_folder, exist_ok=True)

    for i in range(1, filenum + 1):
        # Read entry
        size = struct.unpack_from("<I", mem, offset)[0]
        offset += 4

        file_offset = struct.unpack_from("<I", mem, offset)[0]
        offset += 4

        # Modify name like QuickBMS
        name = f"_{i}.dds"

        # Extract file data
        if file_offset + size <= len(mem):
            file_data = mem[file_offset:file_offset + size]
        else:
            file_data = b''

        # Save file
        with open(os.path.join(output_folder, name), "wb") as out:
            out.write(file_data)

        # Skip 0x30 bytes
        offset += 0x30

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python BafExtract.py <input_baf_file> <output_folder>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_folder = sys.argv[2]
    extract_archive(input_file, output_folder)