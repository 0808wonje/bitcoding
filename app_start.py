import uvicorn

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", reload=False, port=8000)
