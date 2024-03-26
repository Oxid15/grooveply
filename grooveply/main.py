import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI, prebuilt_html

from grooveply.auto import update_statuses
from grooveply.db import create_tables
from grooveply.routers.application import router as application_router
from grooveply.routers.automation import router as automation_router
from grooveply.routers.job_board import router as job_board_router
from grooveply.routers.location import router as location_router
from grooveply.utils import page

app = FastAPI(debug=True)
create_tables()
update_statuses()

router = APIRouter()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def main_page() -> list[AnyComponent]:
    return page("Main Page", [])


app.include_router(router, prefix="/api")
app.include_router(application_router, prefix="/api/application")
app.include_router(automation_router, prefix="/api/automation")
app.include_router(job_board_router, prefix="/api/job_board")
app.include_router(location_router, prefix="/api/location")


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Grooveply"))


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()
