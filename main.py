from fastapi import FastAPI

from src.routes import auth, contacts, users

app = FastAPI()

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Hello world"}
