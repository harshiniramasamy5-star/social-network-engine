from collections import defaultdict, deque
import heapq
from graph import social

# ════════════════════════════════════════════════════════
# 1. BFS — Friend Suggestions
#    Time: O(V + E)  Space: O(V)
#    Real use: LinkedIn "People you may know"
# ════════════════════════════════════════════════════════
def suggest_friends(user_id: str, max_suggestions: int = 5) -> list:
    if user_id not in social.users:
        return []

    visited = {user_id}
    # Level 1 = people user already follows
    level1 = social.graph[user_id]
    visited.update(level1)

    suggestions = defaultdict(int)

    # BFS level 2 — friends of friends
    queue = deque(level1)
    while queue:
        friend = queue.popleft()
        for fof in social.graph[friend]:   # friend of friend
            if fof not in visited:
                suggestions[fof] += 1      # count mutual connections

    # Sort by mutual connection count (most mutuals first)
    ranked = sorted(suggestions.items(), key=lambda x: -x[1])
    return [
        {**social.users[uid], "mutual_connections": count}
        for uid, count in ranked[:max_suggestions]
        if uid in social.users
    ]


# ════════════════════════════════════════════════════════
# 2. DIJKSTRA — Shortest Connection Path
#    Time: O((V + E) log V)  Space: O(V)
#    Real use: LinkedIn "How are you connected?"
# ════════════════════════════════════════════════════════
def shortest_path(start_id: str, end_id: str) -> dict:
    if start_id not in social.users or end_id not in social.users:
        return {"path": [], "hops": -1, "found": False}

    # Min heap: (distance, user_id, path)
    heap = [(0, start_id, [start_id])]
    visited = set()

    while heap:
        dist, current, path = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        if current == end_id:
            return {
                "path": [social.users[u]["name"] for u in path],
                "hops": dist,
                "found": True,
                "user_ids": path
            }

        for neighbor in social.graph[current]:
            if neighbor not in visited:
                heapq.heappush(heap, (dist + 1, neighbor, path + [neighbor]))

    return {"path": [], "hops": -1, "found": False}


# ════════════════════════════════════════════════════════
# 3. MAX HEAP — Top Influencers
#    Time: O(n log k)  Space: O(k)
#    Real use: Twitter trending accounts
# ════════════════════════════════════════════════════════
def get_top_influencers(k: int = 5) -> list:
    # Max heap using negative values (Python heapq is min-heap)
    heap = []
    for uid, info in social.users.items():
        followers = len(social.followers[uid])
        # Push (-followers, uid) so largest followers = highest priority
        heapq.heappush(heap, (-followers, uid))

    top = []
    for _ in range(min(k, len(heap))):
        neg_count, uid = heapq.heappop(heap)
        top.append({
            **social.users[uid],
            "follower_count": -neg_count,
            "rank": len(top) + 1
        })
    return top


# ════════════════════════════════════════════════════════
# 4. DYNAMIC PROGRAMMING — Feed Ranking
#    Time: O(n log n)  Space: O(n)
#    Real use: Instagram feed algorithm
# ════════════════════════════════════════════════════════
def rank_feed(user_id: str, max_posts: int = 10) -> list:
    if user_id not in social.users:
        return []

    following = social.graph[user_id]
    candidate_posts = []

    for followed_id in following:
        for post_id in social.user_posts.get(followed_id, []):
            if post_id in social.posts:
                candidate_posts.append(social.posts[post_id])

    # DP scoring: engagement_score = likes*1 + comments*3 + shares*5
    # weights reflect real platform priorities (shares > comments > likes)
    def engagement_score(post):
        memo = {}
        pid = post["id"]
        if pid not in memo:
            memo[pid] = (
                post["likes"]    * 1 +
                post["comments"] * 3 +
                post["shares"]   * 5
            )
        return memo[pid]

    ranked = sorted(candidate_posts, key=engagement_score, reverse=True)
    return [
        {**p, "engagement_score": engagement_score(p)}
        for p in ranked[:max_posts]
    ]


# ════════════════════════════════════════════════════════
# 5. UNION-FIND — Community Detection
#    Time: O(V * α(V)) ≈ O(V)  Space: O(V)
#    Real use: Facebook friend groups
# ════════════════════════════════════════════════════════
class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank   = {e: 0 for e in elements}

    def find(self, x):
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

def detect_communities() -> list:
    users = list(social.users.keys())
    if not users:
        return []

    uf = UnionFind(users)

    # Union users who follow each other (mutual connection = same community)
    for user in users:
        for followee in social.graph[user]:
            if user in social.followers[followee]:  # mutual follow
                uf.union(user, followee)

    # Group users by their root/community
    communities = defaultdict(list)
    for user in users:
        root = uf.find(user)
        communities[root].append(social.users[user])

    # Sort communities by size (largest first)
    result = sorted(communities.values(), key=len, reverse=True)
    return [
        {"community_id": i+1, "size": len(c), "members": c}
        for i, c in enumerate(result)
    ]


# ════════════════════════════════════════════════════════
# 6. DFS — Mutual Followers
#    Time: O(V + E)  Space: O(V)
# ════════════════════════════════════════════════════════
def get_mutual_followers(user1_id: str, user2_id: str) -> list:
    followers1 = social.followers[user1_id]
    followers2 = social.followers[user2_id]
    mutual_ids = followers1.intersection(followers2)
    return [social.users[uid] for uid in mutual_ids if uid in social.users]