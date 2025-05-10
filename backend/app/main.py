from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base
import os
import traceback

print("JWT_SECRET:", os.getenv("JWT_SECRET"))
print("API_KEY:", os.getenv("API_KEY"))

app = FastAPI(title="To-Do API")

# Run this only when the app starts — ensures DB is ready
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI To-Do app"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "healthy",
            "components": {
                "api": "up",
                "database": "up"
            }
        }
    except Exception as e:
        print("🚨 Health check DB error:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "status": "degraded",
                "components": {
                    "api": "up",
                    "database": "down"
                },
                "error": str(e)
            }
        )

@app.get("/todos", response_model=list[schemas.TodoOut])
def read_todos(db: Session = Depends(get_db)):
    return crud.get_todos(db)

@app.post("/todos", response_model=schemas.TodoOut, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)

@app.put("/todos/{todo_id}", response_model=schemas.TodoOut)
def update(todo_id: int, todo: schemas.TodoBase, db: Session = Depends(get_db)):
    db_todo = crud.update_todo(db, todo_id, todo)
    if not db_todo:
        raise HTTPException(status_code=404, detail="To-do not found")
    return db_todo

@app.delete("/todos/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_todo(db, todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="To-do not found")
    return {"message": "Deleted"}