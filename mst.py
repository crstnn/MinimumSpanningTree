#!/usr/bin/python3.10
import math
from collections import namedtuple
from MinimumSpanningTree.int_set import IntSet
from MinimumSpanningTree.union_by_height_pc import DisjointSet

Edge = namedtuple("Edge", "first_vertex second_vertex weight")
SpecialEdge = namedtuple("SpecialEdge", "first_vertex second_vertex weight is_flipped_vertices")
VertexInformation = namedtuple("VertexInformation", "vertex_id parent_vertex_id parent_edge depth")
GraphInformation = namedtuple("GraphInformation", "number_of_vertices number_of_edges")


class Graph:
    """
    For simple, weighted, undirected, and connected graphs.
    Edge format: G(V, E, W)
    Minimum spanning tree:
        - Calculates the MST using Kruskal's
        - Calculates the second-smallest MST modelled on the LCA problem
    """

    def __init__(self, graph_information: GraphInformation, edges: list[Edge]):
        self.edges: list[Edge] = edges
        self.number_of_vertices: int = graph_information.number_of_vertices
        self.number_of_edges: int = graph_information.number_of_edges

        # MST
        self.mst_edges: list[Edge] = []
        self.mst_weight: int = 0
        self.edges_not_in_mst: list[Edge] = []

        # second-smallest MST
        self.second_smallest_mst_edges: list[Edge] = []
        self.second_smallest_mst_weight: int = 0

    def kruskal(self):
        self.edges = Graph.sort_by_weight(self.edges)

        forest = DisjointSet(self.number_of_vertices + 1)

        for idx, (first_vert, second_vert, weight) in enumerate(self.edges):
            if forest.find(first_vert) != forest.find(second_vert):
                forest.union(first_vert, second_vert)
                self.mst_edges.append(self.edges[idx])
                self.mst_weight += weight
            else:
                # also keep track of the edges not in MST for later calculation of second-best spanning tree
                self.edges_not_in_mst.append(self.edges[idx])

    def smallest_mst(self) -> tuple[list[Edge], int]:
        self.kruskal()
        self.mst_edges = self.sort_edges_by_vertex(self.mst_edges)
        return self.mst_edges, self.mst_weight

    @staticmethod
    def sort_by_weight(st: list[Edge]) -> list[Edge]:
        return sorted(st, key=lambda x: x.weight)

    @staticmethod
    def sort_by_first_vertex(st: list[Edge]) -> list[Edge]:
        return sorted(st, key=lambda x: x.first_vertex)

    @staticmethod
    def sort_by_second_vertex(st: list[Edge]) -> list[Edge]:
        return sorted(st, key=lambda x: x.second_vertex)

    @staticmethod
    def sort_edges_by_vertex(st: list[Edge]) -> list[Edge]:
        # sorted by first vertex, then second vertex
        # provides ordering special property as inbuilt func is 'stable' sort
        return Graph.sort_by_first_vertex(Graph.sort_by_second_vertex(st))

    @staticmethod
    def find_max_edge_between_two_vertices(vert_1: int, vert_2: int, vert_infos: list[VertexInformation]) -> Edge:

        current_u = vert_1
        current_v = vert_2
        max_child = None
        while True:
            if current_u == current_v:
                # LCA reached
                return max_child.parent_edge

            u_info = vert_infos[current_u]
            v_info = vert_infos[current_v]

            if u_info.depth <= v_info.depth:
                if max_child is None or v_info.parent_edge.weight > max_child.parent_edge.weight:
                    max_child = v_info
                current_v = v_info.parent_vertex_id
            if u_info.depth >= v_info.depth:
                if max_child is None or u_info.parent_edge.weight > max_child.parent_edge.weight:
                    max_child = u_info
                current_u = u_info.parent_vertex_id

    @staticmethod
    def _get_adjacent_vertices_lookup_table(edges: list[Edge], number_of_vertices) -> tuple[list[SpecialEdge], ...]:

        lookup_table: tuple[list[SpecialEdge], ...] = tuple([] for _ in range(number_of_vertices + 1))

        for (first_vert, second_vert, weight) in edges:
            lookup_table[second_vert].append(SpecialEdge(second_vert, first_vert, weight, True))
            lookup_table[first_vert].append(SpecialEdge(first_vert, second_vert, weight, False))

        return lookup_table

    @staticmethod
    def _find_edges_for_vertex(vertex, lookup_table: tuple[list, ...]):
        return lookup_table[vertex]

    def second_smallest_mst(self) -> tuple[list[Edge], int]:

        # Kruskal's must have run before calculating second-smallest MST
        if not self.mst_edges:
            self.smallest_mst()

        if len(self.mst_edges) == self.number_of_edges:  # no second-smallest MST
            return self.second_smallest_mst_edges, -1

        adjacent_vertices_table = Graph._get_adjacent_vertices_lookup_table(self.mst_edges, self.number_of_vertices)

        visited_vert_set = IntSet(self.number_of_vertices + 1)

        # arbitrarily chosen first vertex as root of tree
        currently_processing = [1]
        vertex_infos = [None, VertexInformation(1, None, None, 0)] + ([None] * (self.number_of_vertices - 1))

        depth = 0
        # BFS of MST from root to leaves
        while currently_processing:
            depth += 1
            curr_vert = currently_processing.pop()
            visited_vert_set.add(curr_vert)
            edges_for_vertex = Graph._find_edges_for_vertex(curr_vert, adjacent_vertices_table)
            for edge in edges_for_vertex:
                other_vert = edge.second_vertex  # get other vertex
                if other_vert in visited_vert_set:
                    # avoid navigating backwards up the one parent edge
                    continue
                # else every other neighbour of curr_vert must be a child

                # other_vert is child vert
                vertex_infos[other_vert] = VertexInformation(other_vert, curr_vert, edge, depth)
                visited_vert_set.add(other_vert)
                currently_processing.append(other_vert)

        best_difference = math.inf
        best_replacement_pair: tuple[Edge | None, Edge | None] = (None, None)
        for new_edge in self.edges_not_in_mst:
            old_edge = Graph.find_max_edge_between_two_vertices(new_edge.first_vertex,
                                                                new_edge.second_vertex,
                                                                vertex_infos)
            weight_diff = new_edge.weight - old_edge.weight
            if weight_diff <= best_difference:
                best_difference = weight_diff
                best_replacement_pair = (old_edge, new_edge)

        conv_to_normal_edge = lambda x: Edge(x.second_vertex if x.is_flipped_vertices else x.first_vertex,
                                             x.first_vertex if x.is_flipped_vertices else x.second_vertex,
                                             x.weight)

        self.second_smallest_mst_edges = self.mst_edges[:]
        self.second_smallest_mst_edges.remove(conv_to_normal_edge(best_replacement_pair[0]))
        self.second_smallest_mst_edges.append(best_replacement_pair[1])

        # only necessary to make output ordered
        self.second_smallest_mst_edges = Graph.sort_edges_by_vertex(self.second_smallest_mst_edges)

        self.second_smallest_mst_weight = \
            self.mst_weight + best_replacement_pair[1].weight - best_replacement_pair[0].weight

        return self.second_smallest_mst_edges, self.second_smallest_mst_weight
