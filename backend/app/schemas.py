from pydantic import BaseModel

class TodoBase(BaseModel):
    title: str
    done: bool = False

class TodoCreate(TodoBase):
    pass

class TodoOut(TodoBase):
    id: int

    class Config:
        from_attributes = True
