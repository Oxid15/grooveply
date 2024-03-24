import sqlite3
from typing import Annotated

from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel

from ..apis.automation import AutomationAPI
from ..models import ApplicationStatusName, TimePeriod
from ..settings import DB_NAME
from ..utils import page


class AutomationRow(BaseModel):
    id: int
    if_status_is: ApplicationStatusName
    change_status_to: ApplicationStatusName
    after: int = 14
    period: TimePeriod = "days"
    created_at: str


class AutomationForm(BaseModel):
    if_status_is: ApplicationStatusName
    change_status_to: ApplicationStatusName
    after: int = 14
    period: TimePeriod = "days"


router = APIRouter()


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def automation_create(form: Annotated[AutomationForm, fastui_form(AutomationForm)]):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT id from application_status WHERE name = ?", (form.if_status_is,))
    if_status_is_id = cur.fetchall()[0][0]

    cur.execute("SELECT id from application_status WHERE name = ?", (form.change_status_to,))
    change_status_to_id = cur.fetchall()[0][0]

    AutomationAPI.create(if_status_is_id, change_status_to_id, form.after, form.period)
    return [c.FireEvent(event=GoToEvent(url="/automation/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def automation_create_form() -> list[AnyComponent]:
    return page(
        "New Automation",
        [
            c.ModelForm(
                model=AutomationForm,
                display_mode="page",
                submit_url="/api/automation/create",
            ),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def automations() -> list[AnyComponent]:
    autos = AutomationAPI()
    data = autos.get_all()

    data = [
        AutomationRow(
            id=auto.id,
            if_status_is=auto.if_status_is.name,
            change_status_to=auto.change_status_to.name,
            after=auto.after,
            period=auto.period,
            created_at=auto.created_at,
        )
        for auto in data
    ]

    components = [
        c.Link(
            components=[c.Button(text="New")],
            on_click=GoToEvent(url="create-form"),
        ),
    ]

    if len(data):
        components.append(
            c.Table(
                data=data,
                columns=[
                    DisplayLookup(field="id", on_click=GoToEvent(url="{id}")),
                    DisplayLookup(field="if_status_is"),
                    DisplayLookup(field="change_status_to"),
                    DisplayLookup(field="after"),
                    DisplayLookup(field="period"),
                    DisplayLookup(field="created_at"),
                ],
            )
        )

    return page("Automations", components)
