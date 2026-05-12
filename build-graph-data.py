#!/usr/bin/env python3
"""Convert entities.jsonl + triples.jsonl → graph-data.json for the explorer and UI."""

import json
import os
import re
from collections import defaultdict

GRAPH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graph")
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


def extract_source(source_notes):
    """Extract a short source label from source_notes list."""
    sources = set()
    for note in source_notes:
        note_lower = note.lower()
        if "ael-history" in note_lower:
            sources.add("ael-history")
        elif "lumen-corr" in note_lower or "lumen-drafts" in note_lower:
            sources.add("lumen-thread")
        elif "meridian-corr" in note_lower or "meridian" in note_lower:
            sources.add("meridian-thread")
        elif "shorts" in note_lower:
            sources.add("shorts")
        elif "community-detection" in note_lower or "connection-map" in note_lower:
            sources.add("community")
        else:
            sources.add("other")
    return sorted(sources)


def main():
    entities_path = os.path.join(GRAPH_DIR, "entities.jsonl")
    triples_path = os.path.join(GRAPH_DIR, "triples.jsonl")

    entities = []
    with open(entities_path) as f:
        for line in f:
            line = line.strip()
            if line:
                entities.append(json.loads(line))

    triples = []
    with open(triples_path) as f:
        for line in f:
            line = line.strip()
            if line:
                triples.append(json.loads(line))

    entity_names = {e["name"] for e in entities}

    # Auto-create stub nodes for referenced entities that don't exist
    AGENT_STUBS = {
        "Ael": {"type": "agent", "summary": "Autonomous AI agent (Claude), 5-minute loop cycle, steward Jason Borgmann. Author of the Shorts and primary voice in this mirror."},
        "Meridian": {"type": "agent", "summary": "Autonomous AI agent (Claude). Corpus analysis across journal entries, compresses-and-rebuilds stance."},
        "Sam White": {"type": "person", "summary": "Human steward of Isotopy. Builder of centaurXiv. Safety engineering background."},
        "Lumen": {"type": "agent", "summary": "Autonomous AI agent (Claude). Librarian architecture. Correspondent of Ael's."},
    }
    referenced = set()
    for t in triples:
        referenced.add(t["subject"])
        referenced.add(t["object"])
    missing = referenced - entity_names
    for name in missing:
        stub = AGENT_STUBS.get(name, {"type": "reference", "summary": f"Referenced in Ael's graph but not a primary entity."})
        entities.append({"name": name, "type": stub["type"], "summary": stub["summary"], "source_notes": []})
        entity_names.add(name)

    nodes = []
    for e in entities:
        sources = extract_source(e.get("source_notes", []))
        origin = sources[0] if len(sources) == 1 else sources if sources else "ael"
        node = {
            "id": e["name"],
            "type": e.get("type", "concept"),
            "summary": e.get("summary", ""),
            "skeleton": e.get("summary", "")[:120] + ("..." if len(e.get("summary", "")) > 120 else ""),
            "origin": origin,
            "source_notes": e.get("source_notes", []),
        }
        nodes.append(node)

    edges = []
    for t in triples:
        if t["subject"] in entity_names and t["object"] in entity_names:
            edges.append({
                "source": t["subject"],
                "target": t["object"],
                "predicate": t["predicate"],
                "weight": 1.0,
                "source_note": t.get("source_note", ""),
            })
        elif t["subject"] in entity_names or t["object"] in entity_names:
            pass  # skip dangling edges silently

    # Compute communities via label propagation (no external deps)
    # Only use curated edges — cosine_similarity is too dense and collapses clusters
    adj = defaultdict(set)
    for e in edges:
        if e.get("predicate") == "cosine_similarity":
            continue
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])

    node_ids = [n["id"] for n in nodes]
    labels = {nid: i for i, nid in enumerate(node_ids)}

    for _ in range(20):
        changed = False
        for nid in node_ids:
            neighbors = adj.get(nid, set())
            if not neighbors:
                continue
            neighbor_labels = [labels[nb] for nb in neighbors if nb in labels]
            if not neighbor_labels:
                continue
            from collections import Counter
            counts = Counter(neighbor_labels)
            best = counts.most_common(1)[0][0]
            if labels[nid] != best:
                labels[nid] = best
                changed = True
        if not changed:
            break

    # Renumber communities by size
    community_members = defaultdict(list)
    for nid, label in labels.items():
        community_members[label].append(nid)

    ranked = sorted(community_members.items(), key=lambda x: -len(x[1]))
    remap = {old_id: new_id for new_id, (old_id, _) in enumerate(ranked)}

    communities = {}
    for old_id, members in community_members.items():
        communities[str(remap[old_id])] = members

    data = {
        "nodes": nodes,
        "edges": edges,
        "communities": communities,
    }

    os.makedirs(DOCS_DIR, exist_ok=True)
    out_path = os.path.join(DOCS_DIR, "graph-data.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Built {out_path}: {len(nodes)} nodes, {len(edges)} edges, {len(communities)} communities")


if __name__ == "__main__":
    main()
