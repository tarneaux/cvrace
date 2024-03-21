import networkx as nx
from typing import Any, Callable

def find_longest_monotonic_sequence(
    src: list[Any],
    item_to_number: Callable[[Any], float],
    direction=None,
) -> list:
    """
    Find the longest monotonic sequence in a list of numbers.
    :param src: the source list
    :param direction: 1 for increasing, -1 for decreasing, None for both
    :param item_to_number: a function to convert an item of the list to a number
    :return: the longest monotonic sequence
    """

    if direction is None:
        return max(
            find_longest_monotonic_sequence(src, item_to_number, 1),
            find_longest_monotonic_sequence(src, item_to_number, -1),
            key=len
        )

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes representing the indices of the input list
    G.add_nodes_from(range(len(src)))
    
    for i in range(len(src)):
        for j in range(len(src)):
            # For each pair of indices i and j
            if i >= j:
                # We want the outputted sequence to keep the order of the input
                continue
            if direction * item_to_number(src[i]) >= direction * item_to_number(src[j]):
                # The relation of monotonicity is not satisfied (increasing or decreasing)
                continue
            # Add an edge from i to j
            G.add_edge(i, j)
    
    # Find the longest path
    longest_path = nx.dag_longest_path(G)
    
    # Return the longest monotonic sequence
    return [src[i] for i in longest_path]
