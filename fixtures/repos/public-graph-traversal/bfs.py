from collections import deque


def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    frontier = deque([start])
    visited = {start}
    order: list[str] = []
    while frontier:
        node = frontier.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return order
