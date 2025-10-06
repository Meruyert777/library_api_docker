from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List

app = FastAPI(title="Golden Library API")


DATABASE_URL = "sqlite:///books.db"
engine = create_engine(DATABASE_URL, echo=True)


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    year: int


def create_db():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db()

@app.get("/")
def root():
    return {"message": "Library API жұмыс істеп тұр! /books endpoint-ін тексеріңіз."}

@app.get("/books", response_model=List[Book])
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Кітап табылмады")
        return book

@app.post("/books", response_model=Book, status_code=201)
def add_book(book: Book):
    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, new_data: Book):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Кітап табылмады")
        book.title = new_data.title
        book.author = new_data.author
        book.year = new_data.year
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Кітап табылмады")
        session.delete(book)
        session.commit()
        return

