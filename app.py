import heapq
import os
import pickle

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):  # For priority queue
        return self.freq < other.freq

def build_frequency_dict(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq

def build_huffman_tree(freq_dict):
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    return heap[0]

def build_codes(root):
    codes = {}
    def generate_code(node, current_code=""):
        if not node:
            return
        if node.char is not None:
            codes[node.char] = current_code
        generate_code(node.left, current_code + "0")
        generate_code(node.right, current_code + "1")
    generate_code(root)
    return codes

def compress(text, codes):
    return ''.join(codes[ch] for ch in text)

def pad_encoded_text(encoded_text):
    extra_padding = 8 - (len(encoded_text) % 8)
    padded_info = format(extra_padding, "08b")
    encoded_text += '0' * extra_padding
    return padded_info + encoded_text

def get_byte_array(padded_encoded_text):
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

def compress_file(input_path):
    output_path = input_path.replace(".txt", "_compressed.bin")

    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    freq_dict = build_frequency_dict(text)
    root = build_huffman_tree(freq_dict)
    codes = build_codes(root)
    encoded_text = compress(text, codes)
    padded_encoded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_encoded_text)

    with open(output_path, "wb") as output:
        pickle.dump(root, output)  # Save tree
        output.write(bytes(byte_array))

    print(f"Compressed '{input_path}' to '{output_path}'")

def remove_padding(padded_text):
    extra_padding = int(padded_text[:8], 2)
    padded_text = padded_text[8:]
    return padded_text[:-extra_padding]

def decode_text(encoded_text, root):
    decoded = ""
    current = root
    for bit in encoded_text:
        current = current.left if bit == "0" else current.right
        if current.char is not None:
            decoded += current.char
            current = root
    return decoded

def decompress_file(input_path):
    output_path = input_path.replace("_compressed.bin", "_decompressed.txt")

    with open(input_path, "rb") as file:
        root = pickle.load(file)
        bit_string = ""
        byte = file.read(1)
        while byte:
            bits = bin(ord(byte))[2:].rjust(8, '0')
            bit_string += bits
            byte = file.read(1)

    encoded_text = remove_padding(bit_string)
    decoded_text = decode_text(encoded_text, root)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(decoded_text)

    print(f"Decompressed '{input_path}' to '{output_path}'")
if __name__ == "__main__":
    compress_file("example.txt")                      # compress input.txt → input_compressed.bin
    decompress_file("input_compressed.bin")