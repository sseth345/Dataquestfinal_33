import hashlib, time

class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return hashlib.sha256(
            (str(self.index) + str(self.timestamp) + str(self.data) + str(self.prev_hash)).encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def add_block(self, data):
        prev = self.chain[-1]
        block = Block(len(self.chain), time.time(), data, prev.hash)
        self.chain.append(block)
        return block
