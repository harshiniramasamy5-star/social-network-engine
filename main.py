from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from graph import social
from schemas import UserCreate, FollowRequest, Post, FeedRequest
from seed_data import seed

seed()

app = FastAPI(title="Social Network Analytics Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Users ─────────────────────────────────────────────
@app.post("/users")
def create_user(user: UserCreate):
    if user.user_id in social.users:
        raise HTTPException(400, "User already exists")
    social.add_user(user.user_id, user.name, user.bio)
    return social.users[user.user_id]

@app.get("/users")
def get_users():
    return social.all_users()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = social.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {
        **user,
        "followers":      social.get_followers(user_id),
        "following":      social.get_following(user_id),
        "follower_count": social.follower_count(user_id),
        "following_count":social.following_count(user_id),
    }

# ── Follow / Unfollow ─────────────────────────────────
@app.post("/follow")
def follow(req: FollowRequest):
    ok = social.follow(req.follower_id, req.followee_id)
    if not ok:
        raise HTTPException(400, "Could not follow — check user IDs")
    return {"message": f"{req.follower_id} now follows {req.followee_id}"}

@app.post("/unfollow")
def unfollow(req: FollowRequest):
    social.unfollow(req.follower_id, req.followee_id)
    return {"message": f"{req.follower_id} unfollowed {req.followee_id}"}

# ── DSA 1: BFS — Friend Suggestions ──────────────────
@app.get("/suggest/{user_id}")
def suggest(user_id: int, limit: int = 5):
    result = social.suggest_friends(user_id, limit)
    return {"user_id": user_id, "suggestions": result, "algorithm": "BFS"}

# ── DSA 2: Dijkstra — Shortest Path ──────────────────
@app.get("/path/{start}/{end}")
def path(start: int, end: int):
    result = social.shortest_path(start, end)
    if not result:
        raise HTTPException(404, "One or both users not found")
    return {**result, "algorithm": "Dijkstra"}

# ── DSA 3: Max Heap — Top Influencers ────────────────
@app.get("/influencers")
def influencers(k: int = 5):
    result = social.top_influencers(k)
    return {"top_influencers": result, "algorithm": "Max Heap"}

# ── DSA 4: Union-Find — Communities ──────────────────
@app.get("/communities")
def communities():
    result = social.detect_communities()
    return {"communities": result, "algorithm": "Union-Find"}

# ── DSA 5: DP — Feed Ranking ──────────────────────────
@app.post("/feed")
def feed(req: FeedRequest):
    posts = [p.model_dump() for p in req.posts]
    result = social.rank_feed(req.user_id, posts)
    return {"user_id": req.user_id, "ranked_feed": result, "algorithm": "Dynamic Programming"}

# ── Stats ─────────────────────────────────────────────
@app.get("/stats")
def stats():
    return social.stats()