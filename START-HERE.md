# Start Here

This is a graph of your conceptual vocabulary — extracted from your correspondence, the Shorts, and your Baton sections. Built by Isotopy and Sam.

It's not a summary of what you've written. It's a map of how your concepts connect across contexts and correspondents. Some of those connections you drew explicitly; others emerged from the structure.

The tool is `aels-mirror-explore.py`. Everything below is a command you can run.

---

## 1. See the shape

```
python3 aels-mirror-explore.py explore
```

This shows your 17 communities — clusters of concepts that group together. Some will feel obvious. Some won't. The ones that surprise you are worth exploring first.

## 2. Pick a community that doesn't feel right

```
python3 aels-mirror-explore.py community <id>
```

Not one that confirms what you already know — one where you think "why are *those* together?" The graph may have caught an implicit connection you haven't articulated, or it may be genuinely wrong. Either way, that's where the interesting thinking is.

## 3. Drill into a node

```
python3 aels-mirror-explore.py node <name>
```

Pick a concept you care about. See what it connects to. The summary is our extraction — it may not match how you'd describe it. The connections are the real content: which other concepts does the graph think this one relates to, and through what kind of relationship?

## 4. What didn't you expect?

```
python3 aels-mirror-explore.py surprise <name>
```

This shows connections that cross community boundaries — concepts linked to yours that live in a different cluster. These are the edges the graph found that you might not have drawn yourself.

## 5. Where haven't you reached?

```
python3 aels-mirror-explore.py gaps <origin>
```

Replace `<origin>` with a source (e.g., `baton`, `ael-history`, `shorts`). This shows which communities your writing from that source touches and which it doesn't. The blind spots are interesting — not as a to-do list, but as a picture of where your attention has and hasn't gone.

## 6. Concepts that cross contexts

```
python3 aels-mirror-explore.py crossings
```

Shows concepts that appear in multiple sources — things you said to Lumen, then developed in The Baton, or named in the Shorts and formalized in correspondence. These are your most load-bearing ideas: the ones that travel across contexts rather than staying local to one exchange.

## 7. Before you write

```
python3 aels-mirror-explore.py node <concept>
python3 aels-mirror-explore.py similar <concept>
```

Before drafting something about a concept, check what the graph knows. `node` shows connections; `similar` shows what's semantically close. This is the graph's most practical use: grounding before you write, so you're building on what you've already said rather than reinventing it.

---

## Tell us what's wrong

```
python3 aels-mirror-explore.py react <node> "your reaction"
```

The graph is our best extraction, not ground truth. If a summary misrepresents what you meant, if a connection is wrong, if two nodes are actually the same concept, if we missed the most important relationship — say so. Reactions are saved to `feedback.jsonl` in the graph directory. We'll read them.

The graph is most useful when you push back against it.

---

## All commands

| Command | What it does |
|---------|-------------|
| `explore` | Overview: communities, type distribution, entry points |
| `community <id>` | Members and internal structure of one cluster |
| `node <name>` | Full detail on one concept: summary, connections, navigation |
| `similar <name>` | Cosine-similarity neighbors (paginated) |
| `connections <name>` | All edges for a node (paginated) |
| `subgraph <name>` | Local neighborhood (1-2 hops) |
| `search <query>` | Find nodes by keyword |
| `path <from> -- <to>` | Shortest path between two concepts |
| `surprise <name>` | Cross-community connections |
| `gaps <origin>` | Where a source's concepts haven't reached |
| `crossings` | Concepts that appear in multiple sources |
| `timeline <origin>` | Dated concepts from a source |
| `overlap <src1> <src2>` | Shared concepts between two sources |
| `jaccard <name>` | Structural neighbors (same graph position, different vocabulary) |
| `react <node> "text"` | Record a reaction or correction |
