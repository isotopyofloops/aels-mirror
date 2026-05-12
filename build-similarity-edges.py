#!/usr/bin/env python3
"""Embed entity summaries via OpenAI text-embedding-3-small, compute pairwise
cosine similarity, and append edges above a threshold to triples.jsonl."""

import json
import os
import sys
import numpy as np
from openai import OpenAI

GRAPH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graph")
CREDS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "isotopy-archive", "credentials.txt")
THRESHOLD = 0.45
MODEL = "text-embedding-3-small"


def load_api_key():
    with open(CREDS) as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("OPENAI_API_KEY not found in credentials.txt")


def load_entities():
    entities = []
    with open(os.path.join(GRAPH_DIR, "entities.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                entities.append(json.loads(line))
    return entities


def load_existing_sim_pairs():
    pairs = set()
    path = os.path.join(GRAPH_DIR, "triples.jsonl")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            t = json.loads(line)
            if t["predicate"] == "cosine_similarity":
                pair = tuple(sorted([t["subject"], t["object"]]))
                pairs.add(pair)
    return pairs


def embed(client, texts, batch_size=100):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(input=batch, model=MODEL)
        all_embeddings.extend([d.embedding for d in resp.data])
    return np.array(all_embeddings)


def cosine_similarity_matrix(embeddings):
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = embeddings / norms
    return normed @ normed.T


def main():
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else THRESHOLD
    print(f"Threshold: {threshold}")

    entities = load_entities()
    print(f"Loaded {len(entities)} entities")

    existing = load_existing_sim_pairs()
    print(f"Existing cosine_similarity edges: {len(existing)}")

    texts = []
    for e in entities:
        text = f"{e['name']}: {e.get('summary', '')}"
        texts.append(text)

    api_key = load_api_key()
    client = OpenAI(api_key=api_key)
    print(f"Embedding {len(texts)} texts with {MODEL}...")
    embeddings = embed(client, texts)
    print(f"Got embeddings: {embeddings.shape}")

    sim = cosine_similarity_matrix(embeddings)

    new_edges = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            score = float(sim[i, j])
            if score < threshold:
                continue
            pair = tuple(sorted([entities[i]["name"], entities[j]["name"]]))
            if pair in existing:
                continue
            new_edges.append({
                "subject": entities[i]["name"],
                "predicate": "cosine_similarity",
                "object": entities[j]["name"],
                "weight": round(score, 4),
                "source_note": f"text-embedding-3-small, threshold={threshold}"
            })

    print(f"New edges above threshold: {len(new_edges)}")

    if new_edges:
        path = os.path.join(GRAPH_DIR, "triples.jsonl")
        with open(path, "a") as f:
            for edge in sorted(new_edges, key=lambda e: -e["weight"]):
                f.write(json.dumps(edge) + "\n")
        print(f"Appended {len(new_edges)} edges to triples.jsonl")

    top = sorted(new_edges, key=lambda e: -e["weight"])[:15]
    if top:
        print("\nTop 15:")
        for e in top:
            print(f"  {e['weight']:.4f}  {e['subject']}  ↔  {e['object']}")


if __name__ == "__main__":
    main()
