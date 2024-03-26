from typing import Annotated, Optional

from fastapi import Request
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent
from fastui.forms import SelectSearchResponse, fastui_form
from pydantic import BaseModel

from ..apis.job_board import JobBoardAPI
from ..utils import page


class JobBoardForm(BaseModel):
    name: str
    url: Optional[str]


router = APIRouter()


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def create(form: Annotated[JobBoardForm, fastui_form(JobBoardForm)]):
    JobBoardAPI.create(name=form.name, url=form.url)
    return [c.FireEvent(event=GoToEvent(url="/job_board/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def create_form() -> list[AnyComponent]:
    return page(
        "New Job Board",
        [
            c.Button(text="Back", on_click=BackEvent()),
            c.ModelForm(
                model=JobBoardForm,
                display_mode="page",
                submit_url="/api/job_board/create",
            ),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def table() -> list[AnyComponent]:
    data = JobBoardAPI.get_all()

    components = [
        c.Link(
            components=[c.Button(text="New")],
            on_click=GoToEvent(url="create-form"),
        ),
    ]

    if len(data):
        components += [
            c.Table(
                data=data,
                columns=[
                    DisplayLookup(field="id", on_click=GoToEvent(url="{id}")),
                    DisplayLookup(field="name"),
                    DisplayLookup(field="url"),
                    DisplayLookup(field="created_at", mode=DisplayMode.date),
                ],
            ),
        ]

    return page("Locations", components)


@router.get("/search", response_model=SelectSearchResponse)
async def search_view(request: Request, q: str) -> SelectSearchResponse:
    job_boards = JobBoardAPI.get_all()
    return SelectSearchResponse(
        options=[{"value": item.name, "label": item.name} for item in job_boards]
    )
