from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    user_id: int
    name: str
    bio: Optional[str] = ""

class FollowRequest(BaseModel):
    follower_id: int
    followee_id: int

class Post(BaseModel):
    post_id: str
    author_id: int
    content: str
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    recency_score: Optional[float] = 1.0

class FeedRequest(BaseModel):
    user_id: int
    posts: List[Post]