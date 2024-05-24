from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import search
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return 'hello world'


app.include_router(search.router, prefix='/search', tags=['search'])

