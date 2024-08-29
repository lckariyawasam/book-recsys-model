from pydantic import BaseModel

class BookTitle(BaseModel):
    title: str


class BookRequest(BaseModel):
    id: str
    k: int