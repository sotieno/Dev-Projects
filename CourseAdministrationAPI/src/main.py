# main.py

# Import necessary modules and classes
from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder

# Import the get_db instance from dependencies.py
from src.dependencies import get_db

# Import the APIRouter instance from courses.py
from src.routers.courses import router as courses_router

# Create a FastAPI instance
app = FastAPI()

# Include the courses router in the main app
app.include_router(courses_router, dependencies=[Depends(get_db)])
