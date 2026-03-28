import struct
import zlib
import os
import sys

def read_uint32(f):
    return struct.unpack("<I", f.read(4))[0]

def pack_archive(input_baf, dds_folder, output_baf):
    with open(input_baf, "rb") as f:
        # Get compressed size (ZSIZE)
        f.seek(0, os.SEEK_END)
        zsize = f.tell()
        f.seek(0)

        zsize -= 4

        # Read uncompressed size
        size = read_uint32(f)

        # Read compressed data
        comp_data = f.read(zsize)

        # Decompress
        decompressed = zlib.decompress(comp_data)

    print(f"uncompressed size: {size}, actual len: {len(decompressed)}")

    # Work on decompressed data
    mem = bytearray(decompressed)
    offset = 0

    # Read file count
    filenum = struct.unpack_from("<H", mem, offset)[0]
    offset += 2

    print(f"filenum: {filenum}")

    # Jump to 0x50
    offset = 0x50

    for i in range(1, filenum + 1):
        # Read entry
        entry_size = struct.unpack_from("<I", mem, offset)[0]
        offset += 4

        file_offset = struct.unpack_from("<I", mem, offset)[0]
        offset += 4

        print(f"Entry {i}: size {entry_size}, file_offset {file_offset}")

        # Read the DDS file
        dds_file = os.path.join(dds_folder, f"_{i}.dds")
        with open(dds_file, "rb") as df:
            dds_data = df.read()

        if len(dds_data) != entry_size:
            print(f"Warning: DDS file {dds_file} size {len(dds_data)} != expected {entry_size}")

        # Replace in mem
        mem[file_offset:file_offset + entry_size] = dds_data

        # Skip 0x30 bytes
        offset += 0x30

    # Now compress the modified mem
    compressed = zlib.compress(mem)

    # Write to output
    with open(output_baf, "wb") as f:
        f.write(struct.pack("<I", len(mem)))  # uncompressed size
        f.write(compressed)

    print(f"Packed to {output_baf}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python BafPack.py <input_baf_file> <dds_folder>")
        sys.exit(1)
    input_baf = sys.argv[1]
    dds_folder = sys.argv[2]
    output_baf = input_baf.rsplit('.', 1)[0] + "_new.baf"
    pack_archive(input_baf, dds_folder, output_baf)