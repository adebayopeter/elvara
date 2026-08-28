from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    
    
@app.get("/")
def homes():
    return {"message": "Welcome to the Todo API!"}

@app.get("/todos/")
def get_todos():
    return [
        {'id': 1, 'title': 'Buy groceries', 'description': 'Milk, Bread, Eggs', 'completed': False},
        {'id': 2, 'title': 'Clean the house', 'description': 'Vacuum, Dust, Mop', 'completed': True},
        {'id': 3, 'title': 'Finish project', 'description': 'Complete the final report', 'completed': False},
        {'id': 4, 'title': 'Exercise', 'description': 'Go for a run', 'completed': True}
    ]
    
@app.post("/todos/")
def create_todo(todo: Todo):
    return {"message": "Todo created successfully!", "todo": todo}