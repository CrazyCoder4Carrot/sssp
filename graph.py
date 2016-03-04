import os
import sys
class graph:
    def __init__(self, beg_file, csr_file, weight_file):
        with open(beg_file, "r") as f:
            self.beg_pos = map(int, f.read().splitlines())
        f.close()
        with open(csr_file, "r") as f:
            self.csr = map(int, f.read().splitlines())
        f.close()
        with open(weight_file, "r") as f:
            self.weight = map(float, f.read().splitlines())
        f.close()
        self.vertex_count = len(self.beg_pos ) - 1
        self.edge_count = len(self.csr)
