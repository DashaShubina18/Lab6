from collections import deque

import matplotlib.pyplot as plt
import networkx as nx

INF = 10 ** 9

TERMINALS = ["Термінал 1", "Термінал 2"]
WAREHOUSES = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
STORES = [f"Магазин {i}" for i in range(1, 15)]

BASE_EDGES = [
    ("Термінал 1", "Склад 1", 25),
    ("Термінал 1", "Склад 2", 20),
    ("Термінал 1", "Склад 3", 15),
    ("Термінал 2", "Склад 3", 15),
    ("Термінал 2", "Склад 4", 30),
    ("Термінал 2", "Склад 2", 10),
    ("Склад 1", "Магазин 1", 15),
    ("Склад 1", "Магазин 2", 10),
    ("Склад 1", "Магазин 3", 20),
    ("Склад 2", "Магазин 4", 15),
    ("Склад 2", "Магазин 5", 10),
    ("Склад 2", "Магазин 6", 25),
    ("Склад 3", "Магазин 7", 20),
    ("Склад 3", "Магазин 8", 15),
    ("Склад 3", "Магазин 9", 10),
    ("Склад 4", "Магазин 10", 20),
    ("Склад 4", "Магазин 11", 10),
    ("Склад 4", "Магазин 12", 15),
    ("Склад 4", "Магазин 13", 5),
    ("Склад 4", "Магазин 14", 10),
]

REGION = [f"Магазин {i}" for i in range(10, 15)]


def build_network(edges):
    nodes = ["Джерело"] + TERMINALS + WAREHOUSES + STORES + ["Стік"]
    index = {name: i for i, name in enumerate(nodes)}
    capacity = [[0] * len(nodes) for _ in nodes]
    for terminal in TERMINALS:
        capacity[index["Джерело"]][index[terminal]] = INF
    for u, v, c in edges:
        capacity[index[u]][index[v]] += c
    for store in STORES:
        capacity[index[store]][index["Стік"]] = INF
    return nodes, index, capacity


def bfs(capacity_matrix, flow_matrix, source, sink, parent):
    visited = [False] * len(capacity_matrix)
    queue = deque([source])
    visited[source] = True
    while queue:
        current_node = queue.popleft()
        for neighbor in range(len(capacity_matrix)):
            if not visited[neighbor] and capacity_matrix[current_node][neighbor] \
                    - flow_matrix[current_node][neighbor] > 0:
                parent[neighbor] = current_node
                visited[neighbor] = True
                if neighbor == sink:
                    return True
                queue.append(neighbor)
    return False


def edmonds_karp(capacity_matrix, source, sink):
    num_nodes = len(capacity_matrix)
    flow_matrix = [[0] * num_nodes for _ in range(num_nodes)]
    parent = [-1] * num_nodes
    max_flow = 0
    steps = []
    while bfs(capacity_matrix, flow_matrix, source, sink, parent):
        path_flow = float("inf")
        path = [sink]
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            path_flow = min(path_flow, capacity_matrix[previous_node][current_node]
                            - flow_matrix[previous_node][current_node])
            current_node = previous_node
            path.append(current_node)
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            flow_matrix[previous_node][current_node] += path_flow
            flow_matrix[current_node][previous_node] -= path_flow
            current_node = previous_node
        max_flow += path_flow
        steps.append((path[::-1], path_flow))
    return max_flow, flow_matrix, steps


def decompose(flow_matrix, nodes, source, sink):
    flow = [row[:] for row in flow_matrix]
    result = {}
    while True:
        path = [source]
        visited = {source}
        while path[-1] != sink:
            u = path[-1]
            nxt = next((v for v in range(len(nodes)) if flow[u][v] > 0 and v not in visited), None)
            if nxt is None:
                break
            path.append(nxt)
            visited.add(nxt)
        if path[-1] != sink:
            break
        amount = min(flow[path[i]][path[i + 1]] for i in range(len(path) - 1))
        for i in range(len(path) - 1):
            flow[path[i]][path[i + 1]] -= amount
        key = (nodes[path[1]], nodes[path[-2]])
        result[key] = result.get(key, 0) + amount
    return result


def min_cut(capacity_matrix, flow_matrix, source):
    reachable = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in range(len(capacity_matrix)):
            if v not in reachable and capacity_matrix[u][v] - flow_matrix[u][v] > 0:
                reachable.add(v)
                queue.append(v)
    return [(u, v) for u in reachable for v in range(len(capacity_matrix))
            if v not in reachable and capacity_matrix[u][v] > 0]


def draw_network(edges, title, flow=None, index=None):
    graph = nx.DiGraph()
    for u, v, c in edges:
        graph.add_edge(u, v, capacity=c)
    pos = {}
    for i, name in enumerate(TERMINALS):
        pos[name] = (3.5 + i * 7, 2)
    for i, name in enumerate(WAREHOUSES):
        pos[name] = (1.5 + i * 3.67, 1)
    for i, name in enumerate(STORES):
        pos[name] = (i, 0)
    names = {name: name.split()[0][0] + name.split()[1] for name in graph.nodes}
    edge_list = list(graph.edges)
    labels, widths, styles = {}, [], []
    for u, v in edge_list:
        c = graph[u][v]["capacity"]
        if flow is None:
            labels[(u, v)] = str(c)
            widths.append(1.5)
            styles.append("solid")
        else:
            f = flow[index[u]][index[v]]
            labels[(u, v)] = f"{f}/{c}"
            widths.append(3 if f == c else 0.8 if f == 0 else 1.5)
            styles.append("dashed" if f == 0 else "solid")
    plt.figure(figsize=(14, 6))
    nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="skyblue", edgecolors="black")
    nx.draw_networkx_labels(graph, pos, names, font_size=9, font_weight="bold")
    nx.draw_networkx_edges(graph, pos, edgelist=edge_list, width=widths, style=styles,
                           arrows=True, arrowsize=15, node_size=900)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=9, label_pos=0.4)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def analyze(title, edges):
    nodes, index, capacity = build_network(edges)
    source, sink = index["Джерело"], index["Стік"]
    max_flow, flow, steps = edmonds_karp(capacity, source, sink)

    print("=" * 70)
    print(title)
    print("=" * 70)
    print("\nЗбільшуючі шляхи (покроковий розрахунок):")
    total = 0
    for k, (path, amount) in enumerate(steps, 1):
        total += amount
        route = " -> ".join(nodes[v] for v in path[1:-1])
        print(f"{k:2}. {route:<40} +{amount:<3} (разом {total})")
    print(f"\nМаксимальний потік: {max_flow}")

    print("\nПотоки між терміналами та магазинами:")
    print(f"{'Термінал':<12}{'Магазин':<13}{'Фактичний потік':>16}")
    table = decompose(flow, nodes, source, sink)
    for (terminal, store), amount in sorted(table.items(), key=lambda x: (x[0][0], int(x[0][1].split()[1]))):
        print(f"{terminal:<12}{store:<13}{amount:>16}")

    print("\nПотік від терміналів:")
    for terminal in TERMINALS:
        out = sum(flow[index[terminal]][index[w]] for w in WAREHOUSES)
        cap = sum(capacity[index[terminal]][index[w]] for w in WAREHOUSES)
        print(f"{terminal}: {out} з {cap}")

    print("\nОтримано магазинами (потік / пропускна здатність маршруту):")
    for store in STORES:
        got = flow[index[store]][sink]
        cap = sum(capacity[index[w]][index[store]] for w in WAREHOUSES)
        print(f"{store:<12} {got:>3} / {cap}")

    print("\nМінімальний розріз (вузькі місця):")
    cut = min_cut(capacity, flow, source)
    for u, v in sorted(cut):
        print(f"{nodes[u]} -> {nodes[v]}: {capacity[u][v]}")
    print(f"Сума пропускних здатностей розрізу: {sum(capacity[u][v] for u, v in cut)}")

    demand = sum(capacity[index[w]][index[s]] for w in WAREHOUSES for s in REGION)
    delivered = sum(flow[index[s]][sink] for s in REGION)
    print(f"\nРегіон (Магазини 10-14): попит {demand}, доставлено {delivered} "
          f"({delivered / demand * 100:.1f}%)")
    draw_network(edges, f"{title}: потік / пропускна здатність", flow, index)
    return max_flow, demand, delivered


if __name__ == "__main__":
    draw_network(BASE_EDGES, "Логістична мережа: пропускні здатності")
    base = analyze("БАЗОВА ЗАДАЧА", BASE_EDGES)

    variant_edges = [(u, v, c * 2 if v in REGION else c) for u, v, c in BASE_EDGES]
    variant = analyze("ВАРІАНТ 7: попит Магазинів 10-14 збільшено у 2 рази", variant_edges)


    print("ПОРІВНЯННЯ")
    print(f"{'':<34}{'Базова':>10}{'Варіант 7':>12}")
    print(f"{'Максимальний потік':<34}{base[0]:>10}{variant[0]:>12}")
    print(f"{'Попит Магазинів 10-14':<34}{base[1]:>10}{variant[1]:>12}")
    print(f"{'Доставлено в Магазини 10-14':<34}{base[2]:>10}{variant[2]:>12}")
    print(f"{'Задоволено попиту, %':<34}{base[2] / base[1] * 100:>10.1f}{variant[2] / variant[1] * 100:>12.1f}")

