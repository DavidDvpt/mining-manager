from fastapi import FastAPI


app = FastAPI(
    title="Mining Manager API",
    version="0.1.0",
    description="Main API for the Mining Manager backend.",
)


@app.get("/")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello, World!"}
