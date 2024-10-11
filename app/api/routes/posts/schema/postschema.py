from pydantic import BaseModel
from enum import Enum
from typing import Optional

class PostCategory(str, Enum):
    music = "music"
    today = "today"
    blog = "blog"

class PostCreate(BaseModel):
    title : str
    context : str
    category : PostCategory
    isOpen : Optional[bool] = None
    image : Optional[str] = None

class PostsEdit(BaseModel):
    title : str
    context : str
    category : PostCategory
    isOpen : Optional[bool] = None
    image : Optional[str] = None