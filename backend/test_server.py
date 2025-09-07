"""
Simple test server to verify FastAPI setup works
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test server is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
