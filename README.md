# Social Network Analytics Engine

A graph-powered REST API that models a directed social network and exposes five classic DSA algorithms as live endpoints — built end-to-end in Python with FastAPI.

**Live demo:** https://social-network-engine.onrender.com  
**API docs:** https://social-network-engine.onrender.com/docs

---

## What it does

Most social network features — "People You May Know", "Degrees of Separation", trending creators, community clusters — are fundamentally graph problems. This project implements each one from scratch, without libraries like NetworkX, and serves them as a real REST API you can call right now.

| Feature | Algorithm | Endpoint |
|---|---|---|
| Friend suggestions | BFS (breadth-first search) | `GET /suggest/{user_id}` |
| Degrees of separation | Dijkstra's shortest path | `GET /path/{start}/{end}` |
| Top influencers | Max-heap (priority queue) | `GET /influencers?k=5` |
| Community detection | Union-Find with path compression | `GET /communities` |
| Feed ranking | Dynamic programming scoring | `POST /feed` |

---

## Architecture

```
social-network-engine/
├── main.py          # FastAPI app — routes, request/response handling
├── graph.py         # SocialGraph class — adjacency list + reverse index
├── algorithms.py    # BFS, Dijkstra, Max-Heap, Union-Find, DP implementations
├── schemas.py       # Pydantic models for request/response validation
├── seed_data.py     # 12-user seed graph with 37 directed follow edges
├── static/
│   └── index.html   # Interactive frontend served at /
├── requirements.txt
├── render.yaml      # Render deploy config
└── runtime.txt      # Python version pin
```

The graph is stored as two adjacency lists:
- `graph[user_id]` → set of users this user **follows** (outgoing edges)
- `reverse_graph[user_id]` → set of users who **follow** this user (incoming edges)

The reverse index gives **O(1) follower lookups** without a full graph traversal — the same pattern used in production social graphs.

---

## Algorithms in depth

### 1. Friend Suggestions — BFS

```python
# Walk level-1 (people you follow), then level-2 (their follows)
# Count how many mutual connections lead to each level-2 node
# Return ranked by mutual connection count
queue = deque(level1_follows)
while queue:
    friend = queue.popleft()
    for fof in graph[friend]:       # friend-of-friend
        if fof not in visited:
            suggestions[fof] += 1  # mutual connection count
```

This is exactly how LinkedIn's "People You May Know" works at its core: a two-hop BFS where ranking is by mutual overlap.

**Time complexity:** O(V + E) where V = users, E = follow edges

---

### 2. Shortest Path — Dijkstra

```python
# Min-heap: (distance, current_user, path_so_far)
heap = [(0, start_id, [start_id])]
while heap:
    dist, current, path = heapq.heappop(heap)
    if current == end_id:
        return path  # shortest path found
    for neighbor in graph[current]:
        heapq.heappush(heap, (dist + 1, neighbor, path + [neighbor]))
```

Each edge has weight 1 (one follow = one hop), so this finds the minimum number of degrees of separation between any two users. The classic "six degrees of separation" problem.

**Time complexity:** O((V + E) log V)

---

### 3. Top Influencers — Max-Heap

```python
# Python's heapq is a min-heap — negate to simulate max-heap
heap = []
for uid in users:
    heapq.heappush(heap, (-follower_count(uid), uid))

# Pop k times to get top-k influencers in O(n log k)
for _ in range(k):
    neg_count, uid = heapq.heappop(heap)
```

Rather than sorting all users (O(n log n)), a heap gives top-k in **O(n log k)** — the standard production approach for leaderboard queries at scale.

**Time complexity:** O(n log k)

---

### 4. Community Detection — Union-Find

```python
class UnionFind:
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        # Union by rank — keeps tree flat
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
```

Two users are placed in the same community if they **mutually follow each other**. Union-Find with path compression + union by rank gives near-constant-time union/find operations — the same data structure used in Kruskal's MST algorithm.

**Time complexity:** O(E · α(V)) — effectively O(E) since α is the inverse Ackermann function

---

### 5. Feed Ranking — Dynamic Programming

```python
# 5-factor weighted scoring pipeline
dp[1] = likes * 1 + comments * 3 + shares * 5   # engagement
dp[2] = dp[1] + (20 if author in following)      # follow bonus
dp[3] = dp[2] + (15 if mutual follow)            # mutual bonus
dp[4] = dp[3] + (follower_count * 0.1)           # influence signal
dp[5] = dp[4] + recency_score * 5                # recency
```

Each dp[i] builds on dp[i-1], adding one signal at a time. Shares are weighted 5× higher than likes (they indicate stronger intent) — this mirrors the weighting used in real engagement-based ranking systems.

**Time complexity:** O(P) where P = number of posts to rank

---

## API reference

### Users

```
POST   /users                    Create a user
GET    /users                    List all users
GET    /users/{user_id}          Get user + followers/following lists
POST   /follow                   Follow a user
POST   /unfollow                 Unfollow a user
```

### Algorithms

```
GET    /suggest/{user_id}        BFS friend suggestions (limit param)
GET    /path/{start}/{end}       Dijkstra shortest path + degrees of separation
GET    /influencers              Max-heap top-k influencers (k param)
GET    /communities              Union-Find community clusters
POST   /feed                     DP-ranked feed for a user
GET    /stats                    Graph stats: users, edges, density, avg follows
```

### Example responses

**GET /suggest/1**
```json
{
  "user_id": 1,
  "suggestions": [
    {"id": 11, "name": "Lakshmi", "bio": "Software Architect", "mutual_connections": 3},
    {"id": 8,  "name": "Sanjay",  "bio": "Product Manager",    "mutual_connections": 2}
  ],
  "algorithm": "BFS"
}
```

**GET /path/1/12**
```json
{
  "connected": true,
  "path": ["Harshini", "Priya", "Kiran", "Divya", "Rahul"],
  "degrees": 4,
  "algorithm": "Dijkstra"
}
```

**GET /influencers?k=3**
```json
{
  "top_influencers": [
    {"id": 2, "name": "Arjun", "followers": 4, "influence_score": 33.3},
    {"id": 3, "name": "Priya", "followers": 4, "influence_score": 33.3}
  ],
  "algorithm": "Max Heap"
}
```

---

## Seed graph

The API seeds 12 users and 37 directed follow edges on startup:

| ID | Name | Role |
|---|---|---|
| 1 | Harshini | CS Student & Developer |
| 2 | Arjun | ML Engineer at Google |
| 3 | Priya | Full Stack Developer |
| 4 | Ravi | Data Scientist |
| 5 | Meera | UI/UX Designer |
| 6 | Kiran | Backend Engineer |
| 7 | Divya | DevOps Engineer |
| 8 | Sanjay | Product Manager |
| 9 | Ananya | AI Researcher |
| 10 | Vikram | Startup Founder |
| 11 | Lakshmi | Software Architect |
| 12 | Rahul | Cybersecurity Expert |

Graph stats: **12 users · 37 edges · avg 3.08 follows/user · density 0.28**

> Note: the graph is in-memory. Follows created via the API persist for the lifetime of the server process; the seed graph reloads on each cold start.

---

## Run locally

```bash
git clone https://github.com/harshiniramasamy5-star/social-network-engine
cd social-network-engine
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000 for the interactive demo, or http://localhost:8000/docs for the full API explorer.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI |
| Validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| Frontend | Vanilla JS + SVG (no framework) |
| Deploy | Render (web service) |
| CI | Auto-deploy on push via render.yaml |

---

## Design decisions

**Why no NetworkX?** Every algorithm here is implemented from scratch — the point of the project is to demonstrate that I understand BFS, Dijkstra, Union-Find, and heap operations at the code level, not just as library calls.

**Why a reverse adjacency index?** Storing both `graph` (outgoing) and `reverse_graph` (incoming) doubles memory usage but gives O(1) follower lookups. The alternative — scanning all edges to find followers — is O(E) and would be prohibitive at scale. This is the standard production trade-off.

**Why FastAPI over Flask?** FastAPI gives automatic OpenAPI docs, async support, and Pydantic validation with almost no boilerplate. The `/docs` endpoint is a live, clickable API explorer — useful for a demo and for interview walk-throughs.

---

*Built by Harshini Ramasamy · NIT Warangal CSE · [GitHub](https://github.com/harshiniramasamy5-star)*
