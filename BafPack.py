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

    # Read file count
    filenum = struct.unpack_from("<H", mem, 0)[0]
    print(f"filenum: {filenum}")

    toc_start = 0x50
    entry_size = 0x38  # each entry is 56 bytes: 8 bytes + 0x30 payload

    entries = []
    for i in range(1, filenum + 1):
        entry_offset = toc_start + (i - 1) * entry_size
        size = struct.unpack_from("<I", mem, entry_offset)[0]
        file_offset = struct.unpack_from("<I", mem, entry_offset + 4)[0]
        entries.append({
            "index": i,
            "entry_offset": entry_offset,
            "size": size,
            "file_offset": file_offset,
        })
        print(f"Entry {i}: orig_size {size}, orig_offset {file_offset}")

    # Keep original file offsets and sizes. Do in-place replacement only.
    for e in entries:
        i = e["index"]
        dds_file = os.path.join(dds_folder, f"_{i}.dds")

        if not os.path.isfile(dds_file):
            raise FileNotFoundError(f"Missing DDS file: {dds_file}")

        with open(dds_file, "rb") as df:
            dds_data = df.read()

        required_size = e["size"]
        cur_size = len(dds_data)

        if cur_size < required_size:
            print(
                f"Entry {i}: DDS size {cur_size} < required {required_size}, padding with zeros"
            )
            dds_data = dds_data + b"\x00" * (required_size - cur_size)
        elif cur_size > required_size:
            print(
                f"Entry {i}: DDS size {cur_size} > required {required_size}, truncating"
            )
            dds_data = dds_data[:required_size]

        file_offset = e["file_offset"]
        print(f"Entry {i}: replacing at offset {file_offset}, size {required_size}")

        mem[file_offset:file_offset + required_size] = dds_data

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
