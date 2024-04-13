import sqlite3
from typing import Annotated

from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel

from ..apis.application import ApplicationUpdateAPI
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
def create(form: Annotated[AutomationForm, fastui_form(AutomationForm)]):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT id from application_status WHERE name = ?", (form.if_status_is,))
    if_status_is_id = cur.fetchall()[0][0]

    cur.execute("SELECT id from application_status WHERE name = ?", (form.change_status_to,))
    change_status_to_id = cur.fetchall()[0][0]

    AutomationAPI.create(if_status_is_id, change_status_to_id, form.after, form.period)
    return [c.FireEvent(event=GoToEvent(url="/automation/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def create_form() -> list[AnyComponent]:
    return page(
        "New Automation",
        [
            c.Button(text="Back", on_click=BackEvent()),
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
                    DisplayLookup(field="id", on_click=GoToEvent(url="/automation/{id}")),
                    DisplayLookup(field="if_status_is"),
                    DisplayLookup(field="change_status_to"),
                    DisplayLookup(field="after"),
                    DisplayLookup(field="period"),
                    DisplayLookup(field="created_at"),
                ],
            )
        )

    return page("Automations", components)


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def automation(id) -> list[AnyComponent]:
    auto = AutomationAPI.get(id)
    updates = ApplicationUpdateAPI.get_latest_by_auto(id, 10)

    components = [
        c.Link(
            components=[
                c.Button(
                    text="Delete",
                    named_style="warning",
                    on_click=PageEvent(name="del-confirmation"),
                ),
                c.Modal(
                    title="Delete",
                    body=[
                        c.Paragraph(text="Are you sure?"),
                        c.Form(
                            form_fields=[],
                            submit_url=f"/api/automation/delete/{id}",
                            loading=[c.Spinner(text="Okay...")],
                            footer=[],
                            submit_trigger=PageEvent(name="del-confirmation-submit"),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Cancel",
                            named_style="secondary",
                            on_click=PageEvent(name="del-confirmation", clear=True),
                        ),
                        c.Button(
                            text="Delete",
                            named_style="warning",
                            on_click=PageEvent(name="del-confirmation-submit"),
                        ),
                    ],
                    open_trigger=PageEvent(name="del-confirmation"),
                ),
            ]
        ),
        c.Paragraph(text=f"Created: {auto.created_at}"),
        c.Paragraph(
            text=f"If status is {auto.if_status_is.name} then"
            f" changes status to {auto.change_status_to.name}"
            f" after {auto.after} {auto.period}"
        ),
        (
            c.Table(
                data=updates,
                columns=[
                    DisplayLookup(
                        field="application_id",
                        on_click=GoToEvent(url="/application/{application_id}/details"),
                    ),
                    DisplayLookup(field="created_at", mode=DisplayMode.date),
                ],
            )
            if len(updates)
            else c.Paragraph(text="No updates triggered by this automation yet")
        ),
    ]

    return page("Automation", components)


@router.post("/delete/{id}", response_model=FastUI, response_model_exclude_none=True)
def delete(id):
    AutomationAPI.delete(id)
    return [c.FireEvent(event=GoToEvent(url="/automation/"))]
