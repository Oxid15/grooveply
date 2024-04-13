import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui import prebuilt_html
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent

from grooveply.apis.application import ApplicationUpdateAPI
from grooveply.auto import update_statuses
from grooveply.db import create_tables
from grooveply.migrations import apply_migrations
from grooveply.routers.application import router as application_router
from grooveply.routers.automation import router as automation_router
from grooveply.routers.employer import router as employer_router
from grooveply.routers.job_board import router as job_board_router
from grooveply.routers.location import router as location_router
from grooveply.utils import page

app = FastAPI(debug=True)

create_tables()
apply_migrations()
update_statuses()

router = APIRouter()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def main_page() -> list[AnyComponent]:
    latest_updates = ApplicationUpdateAPI.get_latest(10)
    components = [
        c.Heading(text="Latest Updates", level=2),
    ]
    if len(latest_updates):
        components.extend(
            [
                c.Table(
                    data=latest_updates,
                    columns=[
                        DisplayLookup(field="triggerer"),
                        DisplayLookup(
                            field="employer",
                            on_click=GoToEvent(url="application/{application_id}/details"),
                        ),
                        DisplayLookup(field="description"),
                        DisplayLookup(field="created_at", mode=DisplayMode.date),
                    ],
                ),
            ]
        )
    else:
        components.append(c.Paragraph(text="No updates yet"))

    return page("Main Page", components)


app.include_router(router, prefix="/api")
app.include_router(application_router, prefix="/api/application")
app.include_router(automation_router, prefix="/api/automation")
app.include_router(employer_router, prefix="/api/employer")
app.include_router(job_board_router, prefix="/api/job_board")
app.include_router(location_router, prefix="/api/location")


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Grooveply"))


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()
