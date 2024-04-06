# -------------------------------- PYTHON IMPORTS --------------------------------#
# -------------------------------- FASTAPI IMPORTS --------------------------------#
from fastapi import FastAPI

# -------------------------------- SQL ALCHEMY IMPORTS --------------------------------#
# -------------------------------- ROUTES IMPORTS --------------------------------#
from routes.user.routes import user_route
from routes.coverage.routes import coverage_route

# -------------------------------- LOCAL IMPORTS --------------------------------#
from data_seeder import start_data_seeding

# FASTAPI application initialization
app = FastAPI()

# including routers
app.include_router(user_route)
app.include_router(coverage_route)


@app.on_event("startup")
async def startup_event():
    start_data_seeding()
