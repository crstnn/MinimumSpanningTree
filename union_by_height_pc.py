#!/usr/bin/python3.10
class DisjointSet:
    """Union by height with path compression"""

    def __init__(self, n: int) -> None:
        self.parent: list[int] = [-1] * n

    def __contains__(self, item):
        return self.parent[item] != -1

    def union(self, a: int, b: int) -> None:
        root_a: int = self.find(a)
        root_b: int = self.find(b)

        if root_a == root_b: return

        height_a = -self.parent[root_a]
        height_b = -self.parent[root_b]

        if height_a > height_b:
            self.parent[root_b] = root_a
        elif height_a < height_b:
            self.parent[root_a] = root_b
        else:
            self.parent[root_a] = root_b
            self.parent[root_b] = -(height_b + 1)

    def find(self, a: int) -> int:
        """Finds the root of the subtree containing `a`"""
        if self.parent[a] < 0:
            return a
        else:
            self.parent[a] = self.find(self.parent[a])
            return self.parent[a]
