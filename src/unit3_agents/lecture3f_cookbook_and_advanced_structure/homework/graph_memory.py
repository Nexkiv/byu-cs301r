import json
import re
import time
from collections import deque
from pathlib import Path

import tiktoken


def _now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')


class GraphMemory:
    def __init__(self, storage_path: Path = Path('.graph_memory/graph.json')):
        self._path = storage_path
        self._nodes: dict[str, dict] = {}
        self._edges: list[dict] = []
        try:
            self._encoding = tiktoken.encoding_for_model('gpt-5-mini')
        except Exception:
            self._encoding = None
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text())
        self._nodes = {n['id']: n for n in data.get('nodes', [])}
        self._edges = data.get('edges', [])

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'nodes': list(self._nodes.values()),
            'edges': self._edges,
        }
        self._path.write_text(json.dumps(data, indent=2))

    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0
        if self._encoding is None:
            return max(1, len(text) // 4)
        return len(self._encoding.encode(text))

    # --- Node CRUD ---

    def add_node(self, label: str, node_type: str, description: str) -> str:
        node_id = _slugify(label)
        if node_id in self._nodes:
            self._nodes[node_id]['mentions'] += 1
            if description:
                self._nodes[node_id]['description'] = description
            self.save()
            return f'Node "{label}" already exists (id={node_id}), incremented mentions to {self._nodes[node_id]["mentions"]}.'

        self._nodes[node_id] = {
            'id': node_id,
            'label': label,
            'type': node_type,
            'description': description,
            'first_mentioned': _now(),
            'mentions': 1,
        }
        self.save()
        return f'Created node "{label}" (id={node_id}, type={node_type}).'

    def get_node(self, node_id: str) -> dict | None:
        return self._nodes.get(node_id) or self._nodes.get(_slugify(node_id))

    def update_node(self, node_id: str, description: str) -> str:
        node = self.get_node(node_id)
        if not node:
            return f'Node "{node_id}" not found.'
        node['description'] = description
        self.save()
        return f'Updated node "{node["label"]}".'

    # --- Edge CRUD ---

    def add_edge(self, source: str, target: str, relationship: str, context: str) -> str:
        source_id = _slugify(source)
        target_id = _slugify(target)

        if source_id not in self._nodes:
            return f'Source node "{source}" not found. Add it first with add_node.'
        if target_id not in self._nodes:
            return f'Target node "{target}" not found. Add it first with add_node.'

        for edge in self._edges:
            if (edge['source'] == source_id and edge['target'] == target_id
                    and edge['relationship'] == relationship):
                edge['weight'] += 1
                edge['context'] = context
                self.save()
                return f'Edge "{source_id} --[{relationship}]--> {target_id}" already exists, weight increased to {edge["weight"]}.'

        self._edges.append({
            'source': source_id,
            'target': target_id,
            'relationship': relationship,
            'context': context,
            'weight': 1,
        })
        self.save()
        return f'Created edge: {source_id} --[{relationship}]--> {target_id}.'

    # --- Retrieval ---

    def get_connections(self, node_id: str, depth: int = 1) -> str:
        node_id = _slugify(node_id)
        node = self._nodes.get(node_id)
        if not node:
            return f'Node "{node_id}" not found.'

        visited = set()
        current_level = {node_id}
        lines = [f'Connections for "{node["label"]}" (depth={depth}):']

        for d in range(depth):
            next_level = set()
            for nid in current_level:
                if nid in visited:
                    continue
                visited.add(nid)
                for edge in self._edges:
                    if edge['source'] == nid:
                        other = edge['target']
                        other_node = self._nodes.get(other, {})
                        lines.append(
                            f'  {"  " * d}{self._nodes.get(nid, {}).get("label", nid)} '
                            f'--[{edge["relationship"]}]--> '
                            f'{other_node.get("label", other)}'
                        )
                        next_level.add(other)
                    elif edge['target'] == nid:
                        other = edge['source']
                        other_node = self._nodes.get(other, {})
                        lines.append(
                            f'  {"  " * d}{other_node.get("label", other)} '
                            f'--[{edge["relationship"]}]--> '
                            f'{self._nodes.get(nid, {}).get("label", nid)}'
                        )
                        next_level.add(other)
            current_level = next_level - visited

        if len(lines) == 1:
            lines.append('  (no connections)')
        return '\n'.join(lines)

    def search_nodes(self, query: str, limit: int = 5) -> str:
        query_lower = query.lower()
        scored = []
        for node in self._nodes.values():
            text = f'{node["label"]} {node["type"]} {node["description"]}'.lower()
            score = 0
            for token in query_lower.split():
                if token in text:
                    score += 1
            if score > 0:
                scored.append((score, node['mentions'], node))

        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        results = scored[:limit]

        if not results:
            return f'No nodes matching "{query}".'

        lines = [f'Search results for "{query}":']
        for score, mentions, node in results:
            lines.append(
                f'  - {node["label"]} (id={node["id"]}, type={node["type"]}, '
                f'mentions={node["mentions"]}): {node["description"][:120]}'
            )
        return '\n'.join(lines)

    def find_path(self, source: str, target: str) -> str:
        source_id = _slugify(source)
        target_id = _slugify(target)

        if source_id not in self._nodes:
            return f'Source node "{source}" not found.'
        if target_id not in self._nodes:
            return f'Target node "{target}" not found.'
        if source_id == target_id:
            return f'Source and target are the same node.'

        # Build adjacency list (bidirectional)
        adj: dict[str, list[tuple[str, dict]]] = {}
        for edge in self._edges:
            adj.setdefault(edge['source'], []).append((edge['target'], edge))
            adj.setdefault(edge['target'], []).append((edge['source'], edge))

        # BFS
        queue = deque([(source_id, [source_id])])
        visited = {source_id}

        while queue:
            current, path = queue.popleft()
            for neighbor, edge in adj.get(current, []):
                if neighbor in visited:
                    continue
                new_path = path + [neighbor]
                if neighbor == target_id:
                    return self._format_path(new_path)
                visited.add(neighbor)
                queue.append((neighbor, new_path))

        return f'No path found between "{source}" and "{target}".'

    def _format_path(self, path: list[str]) -> str:
        lines = ['Path found:']
        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            src_label = self._nodes[src]['label']
            tgt_label = self._nodes[tgt]['label']
            edge = self._find_edge(src, tgt)
            rel = edge['relationship'] if edge else '?'
            lines.append(f'  {src_label} --[{rel}]--> {tgt_label}')
        return '\n'.join(lines)

    def _find_edge(self, a: str, b: str) -> dict | None:
        for edge in self._edges:
            if (edge['source'] == a and edge['target'] == b) or \
               (edge['source'] == b and edge['target'] == a):
                return edge
        return None

    # --- Prompt Assembly ---

    def build_context(self, query: str, max_tokens: int = 500) -> str:
        if not self._nodes:
            return ''

        query_lower = query.lower()
        scored_nodes = []
        for node in self._nodes.values():
            text = f'{node["label"]} {node["type"]} {node["description"]}'.lower()
            score = 0
            for token in query_lower.split():
                if token in text:
                    score += 1
            score += node['mentions'] * 0.1
            if score > 0:
                scored_nodes.append((score, node))

        scored_nodes.sort(key=lambda x: x[0], reverse=True)

        # Take top relevant nodes and expand their neighborhoods
        context_parts = []
        included_nodes = set()
        token_count = 0

        for _, node in scored_nodes[:5]:
            if token_count >= max_tokens:
                break
            node_text = f'{node["label"]} ({node["type"]}): {node["description"]}'
            node_tokens = self._count_tokens(node_text)
            if token_count + node_tokens > max_tokens:
                continue
            context_parts.append(node_text)
            token_count += node_tokens
            included_nodes.add(node['id'])

            # Add edges for this node
            for edge in self._edges:
                if token_count >= max_tokens:
                    break
                if edge['source'] == node['id'] or edge['target'] == node['id']:
                    other_id = edge['target'] if edge['source'] == node['id'] else edge['source']
                    other = self._nodes.get(other_id, {})
                    edge_text = (
                        f'  -> {edge["relationship"]} -> {other.get("label", other_id)}'
                        f' ({edge["context"][:80]})'
                    )
                    edge_tokens = self._count_tokens(edge_text)
                    if token_count + edge_tokens <= max_tokens:
                        context_parts.append(edge_text)
                        token_count += edge_tokens

        if not context_parts:
            return ''
        return '\n'.join(context_parts)

    # --- Stats & Export ---

    def get_summary(self) -> str:
        if not self._nodes:
            return 'Graph is empty. No nodes or edges yet.'

        # Count connections per node
        conn_count: dict[str, int] = {}
        for edge in self._edges:
            conn_count[edge['source']] = conn_count.get(edge['source'], 0) + 1
            conn_count[edge['target']] = conn_count.get(edge['target'], 0) + 1

        top_connected = sorted(conn_count.items(), key=lambda x: x[1], reverse=True)[:5]

        lines = [
            f'Graph: {len(self._nodes)} nodes, {len(self._edges)} edges',
            '',
            'Most connected nodes:',
        ]
        for node_id, count in top_connected:
            node = self._nodes.get(node_id, {})
            lines.append(f'  - {node.get("label", node_id)} ({count} connections)')

        type_counts: dict[str, int] = {}
        for node in self._nodes.values():
            t = node.get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        lines.append('')
        lines.append('Node types:')
        for t, c in sorted(type_counts.items()):
            lines.append(f'  - {t}: {c}')

        return '\n'.join(lines)

    def export_dot(self) -> str:
        lines = ['digraph GraphMemory {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=rounded];')
        lines.append('')

        for node in self._nodes.values():
            label = node['label'].replace('"', '\\"')
            ntype = node.get('type', '')
            lines.append(f'  "{node["id"]}" [label="{label}\\n({ntype})"];')

        lines.append('')
        for edge in self._edges:
            rel = edge['relationship'].replace('"', '\\"')
            lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{rel}"];')

        lines.append('}')
        return '\n'.join(lines)
