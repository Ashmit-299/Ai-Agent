# app/analytics_jinja.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user
from core.database import DatabaseManager

router = APIRouter(prefix="/jinja-dashboard", tags=["Jinja Dashboard"],
                    dependencies=[Depends(get_current_user)])

templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def dashboard(request: Request):
    data = DatabaseManager.get_analytics_data()
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": data})