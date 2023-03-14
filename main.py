from fastapi import Depends, FastAPI
from routers import category, item, user
from dependencies import get_db
import uvicorn


app = FastAPI(dependencies=[Depends(get_db)])


app.include_router(category.router)
app.include_router(item.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
