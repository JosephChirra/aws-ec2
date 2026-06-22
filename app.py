from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Sample AWS EC2 FastAPI App")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on AWS EC2! this is Version 2.1.2"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
