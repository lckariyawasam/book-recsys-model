from pydantic import BaseModel

class BookTitle(BaseModel):
    title: str