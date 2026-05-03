from collections import defaultdict, deque
import heapq

class SocialGraph:

    def __init__(self):
        self.graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self.users = {}

    def add_user(self, user_id: int, name: str, bio: str = ""):
        self.users[user_id] = {"id": user_id, "name": name, "bio": bio}
        self.graph[user_id]
        self.reverse_graph[user_id]

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def all_users(self):
        return list(self.users.values())

    def follow(self, follower_id: int, followee_id: int):
        if follower_id == followee_id:
            return False
        if follower_id not in self.users or followee_id not in self.users:
            return False
        self.graph[follower_id].add(followee_id)
        self.reverse_graph[followee_id].add(follower_id)
        return True

    def unfollow(self, follower_id: int, followee_id: int):
        self.graph[follower_id].discard(followee_id)
        self.reverse_graph[followee_id].discard(follower_id)

    def get_following(self, user_id: int):
        return [self.users[uid] for uid in self.graph[user_id] if uid in self.users]

    def get_followers(self, user_id: int):
        return [self.users[uid] for uid in self.reverse_graph[user_id] if uid in self.users]

    def follower_count(self, user_id: int):
        return len(self.reverse_graph[user_id])

    def following_count(self, user_id: int):
        return len(self.graph[user_id])

    def is_following(self, follower_id: int, followee_id: int):
        return followee_id in self.graph[follower_id]

    def suggest_friends(self, user_id: int, max_suggestions: int = 5):
        if user_id not in self.users:
            return []

        visited = {user_id}
        following = self.graph[user_id]
        visited.update(following)

        suggestions = defaultdict(int)

        queue = deque(following)
        while queue:
            current = queue.popleft()
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    suggestions[neighbor] += 1
                    visited.add(neighbor)

        ranked = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return [
            {**self.users[uid], "mutual_connections": count}
            for uid, count in ranked[:max_suggestions]
            if uid in self.users
        ]

    def shortest_path(self, start_id: int, end_id: int):
        if start_id not in self.users or end_id not in self.users:
            return None

        distances = {uid: float('inf') for uid in self.users}
        distances[start_id] = 0
        previous = {uid: None for uid in self.users}
        heap = [(0, start_id)]

        while heap:
            dist, current = heapq.heappop(heap)
            if current == end_id:
                break
            if dist > distances[current]:
                continue
            for neighbor in self.graph[current]:
                new_dist = distances[current] + 1
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(heap, (new_dist, neighbor))

        if distances[end_id] == float('inf'):
            return {"connected": False, "path": [], "degrees": -1}

        path, current = [], end_id
        while current is not None:
            path.append(self.users[current]["name"])
            current = previous[current]
        path.reverse()

        return {
            "connected": True,
            "path": path,
            "degrees": distances[end_id]
        }

    def top_influencers(self, k: int = 5):
        heap = []
        for uid in self.users:
            count = self.follower_count(uid)
            heapq.heappush(heap, (-count, uid))

        result = []
        for _ in range(min(k, len(heap))):
            neg_count, uid = heapq.heappop(heap)
            result.append({
                **self.users[uid],
                "followers": -neg_count,
                "following": self.following_count(uid),
                "influence_score": round(-neg_count / max(1, len(self.users)) * 100, 1)
            })
        return result

    def detect_communities(self):
        parent = {uid: uid for uid in self.users}
        rank = {uid: 0 for uid in self.users}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            if rank[px] == rank[py]:
                rank[px] += 1

        for uid in self.users:
            for neighbor in self.graph[uid]:
                if uid in self.graph.get(neighbor, set()):
                    union(uid, neighbor)

        communities = defaultdict(list)
        for uid in self.users:
            communities[find(uid)].append(self.users[uid])

        return [
            {"community_id": i+1, "size": len(members), "members": members}
            for i, members in enumerate(communities.values())
            if len(members) > 0
        ]

    def rank_feed(self, user_id: int, posts: list):
        following = self.graph[user_id]

        scored = []
        for post in posts:
            author_id = post.get("author_id")

            dp = [0.0] * 6
            dp[1] = post.get("likes", 0) * 1.0 + \
                    post.get("comments", 0) * 2.0 + \
                    post.get("shares", 0) * 3.0
            dp[2] = dp[1] + (20.0 if author_id in following else 0.0)
            dp[3] = dp[2] + (15.0 if user_id in self.graph.get(author_id, set()) else 0.0)
            dp[4] = dp[3] + (self.follower_count(author_id) * 0.1)
            dp[5] = dp[4] + post.get("recency_score", 0) * 5.0

            scored.append({**post, "feed_score": round(dp[5], 2)})

        return sorted(scored, key=lambda x: x["feed_score"], reverse=True)

    def stats(self):
        total_edges = sum(len(v) for v in self.graph.values())
        return {
            "total_users": len(self.users),
            "total_connections": total_edges,
            "avg_following": round(total_edges / max(1, len(self.users)), 2),
            "density": round(total_edges / max(1, len(self.users) * (len(self.users)-1)), 4)
        }

social = SocialGraph()
