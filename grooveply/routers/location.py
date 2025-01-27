from typing import Annotated

from fastapi import Request
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastui.forms import SelectSearchResponse, fastui_form
from pydantic import BaseModel

from ..apis.location import LocationAPI
from ..utils import page


class LocationForm(BaseModel):
    name: str


router = APIRouter()


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def location_create(form: Annotated[LocationForm, fastui_form(LocationForm)]):
    LocationAPI.create(name=form.name)
    return [c.FireEvent(event=BackEvent())]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def location_create_form() -> list[AnyComponent]:
    return page(
        "New Location",
        [
            c.Button(text="Back", on_click=BackEvent()),
            c.ModelForm(
                model=LocationForm,
                display_mode="page",
                submit_url="/api/location/create",
            ),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def applications() -> list[AnyComponent]:
    data = LocationAPI.get_all()

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
                    DisplayLookup(field="id"),
                    DisplayLookup(field="name"),
                    DisplayLookup(field="created_at"),
                ],
            ),
        ]

    return page("Locations", components)


@router.get("/search", response_model=SelectSearchResponse)
async def search_view(request: Request, q: str) -> SelectSearchResponse:
    locations = LocationAPI.get_all()
    return SelectSearchResponse(
        options=[{"value": loc.name, "label": loc.name} for loc in locations]
    )
