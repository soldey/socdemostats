from app import app
from app.api.endpoints import units, indicators


app.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
# app.include_router(population.router, prefix="/population", tags=["population"])
app.include_router(units.router, prefix="/units", tags=["units"])
