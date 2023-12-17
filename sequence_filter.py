import networkx as nx

def find_longest_monotonic_sequence(
        src: list,
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
            find_longest_monotonic_sequence(src, 1),
            find_longest_monotonic_sequence(src, -1),
            key=len
        )
    
    # Create a graph
    G = nx.DiGraph()
    G.add_nodes_from(range(len(src)))
    
    # Add edges
    for i in range(len(src)):
        for j in range(len(src)):
            if i >= j or direction * src[i][0] >= direction * src[j][0]:
                continue
            if direction * src[i][1] < direction * src[j][1]:
                G.add_edge(i, j)
    
    # Find the longest path
    longest_path = nx.dag_longest_path(G)
    
    # Return the longest monotonic sequence
    return [src[i] for i in longest_path]
