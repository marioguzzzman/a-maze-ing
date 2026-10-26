
graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": [],
    "F": []
}

def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()

    # Mark the current node as visited
    visited.add(node)
    print(node, end=" ")

    # Explore each unvisited neighbor
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

# Start DFS at node A
dfs(graph, "A")
