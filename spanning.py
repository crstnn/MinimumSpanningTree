#!/usr/bin/python3.10
import sys
from MinimumSpanningTree.mst import Graph, Edge, GraphInformation


def main() -> None:
    """
    Command line version of MST problem
    """
    file_name: str = sys.argv[1]
    edges: list[Edge] = []

    with open(file_name) as file:
        gi = GraphInformation(*map(int, file.readline().rsplit(" ")))
        while line := file.readline():
            edges.append(Edge(*map(int, line.rsplit(" "))))

    graph = Graph(gi, edges)

    mst_triplets, mst_weight = graph.smallest_mst()
    second_mst_triplets, second_mst_weight = graph.second_smallest_mst()

    with open("output_spanning.txt", "w+") as output_file:
        output_file.write("Smallest Spanning Tree Weight = {}\n".format(str(mst_weight)))
        output_file.write("#List of edges in the smallest spanning tree:\n")
        output_file.writelines("{}\n".format(' '.join(map(str, el))) for el in mst_triplets)

        output_file.write("Second-smallest Spanning Tree Weight = {}\n".format(str(second_mst_weight)))
        output_file.write("#List of edges in the second smallest spanning tree:\n")
        output_file.writelines("{}\n".format(' '.join(map(str, el))) for el in second_mst_triplets)


if __name__ == "__main__":
    main()
