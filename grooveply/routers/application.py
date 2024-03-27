import sqlite3
from typing import Annotated, Optional

import pendulum
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent
from fastui.forms import Textarea, fastui_form
from pydantic import BaseModel, Field, create_model

from ..apis.application import ApplicationAPI, ApplicationUpdateAPI
from ..apis.employer import EmployerAPI
from ..models import ApplicationStatusName
from ..settings import DB_NAME, TZ
from ..utils import page


class ApplicationForm(BaseModel):
    employer_name: str
    app_status_name: ApplicationStatusName = "APPLIED"
    description: Annotated[str | None, Textarea(rows=5)] = Field(None)
    url: Optional[str] = None
    location: Optional[str] = Field(None, json_schema_extra={"search_url": "/api/location/search"})
    job_board: Optional[str] = Field(
        None, json_schema_extra={"search_url": "/api/job_board/search"}
    )


class ApplicationUpdateForm(BaseModel):
    app_status_name: ApplicationStatusName
    description: Annotated[str | None, Textarea(rows=5)] = Field(None)
    url: str = None


class ApplicationRow(BaseModel):
    id: int
    status: str
    employer: str
    location: Optional[str]
    job_board: Optional[str]
    description: Optional[str] = None
    created_at: str


router = APIRouter()


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def application_create(form: Annotated[ApplicationForm, fastui_form(ApplicationForm)]):
    # Creating even if exists, retrieving id anyway
    employer_id = EmployerAPI.create(form.employer_name)

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("SELECT id FROM application_status" " WHERE name = ?", (form.app_status_name,))
    status_id = cur.fetchall()[0][0]

    if form.location is not None:
        cur.execute("SELECT id FROM location WHERE name = ?", (form.location,))
        location_id = cur.fetchall()[0][0]
    else:
        location_id = None

    if form.job_board is not None:
        cur.execute("SELECT id FROM job_board WHERE name = ?", (form.job_board,))
        job_board_id = cur.fetchall()[0][0]
    else:
        job_board_id = None

    ApplicationAPI.create(
        employer_id, status_id, location_id, job_board_id, form.description, form.url
    )
    return [c.FireEvent(event=GoToEvent(url="/application/"))]


@router.post("/update/{id}", response_model=FastUI, response_model_exclude_none=True)
def application_update(
    id, form: Annotated[ApplicationUpdateForm, fastui_form(ApplicationUpdateForm)]
):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("SELECT id FROM application_status" " WHERE name = ?", (form.app_status_name,))
    new_status_id = cur.fetchall()[0][0]

    cur.execute("SELECT status_id from application WHERE id = ?", (id,))
    old_status_id = cur.fetchall()[0][0]

    if new_status_id != old_status_id:
        status_updated_at = pendulum.now(tz=TZ)
    else:
        status_updated_at = None

    ApplicationAPI.update(id, new_status_id, status_updated_at, form.description, form.url)
    return [c.FireEvent(event=GoToEvent(url="/application/"))]


@router.post("/delete/{id}", response_model=FastUI, response_model_exclude_none=True)
def application_delete(id):
    ApplicationAPI.delete(id)
    return [c.FireEvent(event=GoToEvent(url="/application/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def application_create_form() -> list[AnyComponent]:
    return page(
        "New Application",
        [
            c.Button(text="Back", on_click=BackEvent()),
            c.ModelForm(
                model=ApplicationForm,
                display_mode="page",
                submit_url="/api/application/create",
            ),
        ],
    )


@router.get("/update-form/{id}", response_model=FastUI, response_model_exclude_none=True)
def application_update_form(id) -> list[AnyComponent]:
    app = ApplicationAPI.get(id)
    update_form = create_model(
        "ApplicationUpdateForm",
        app_status_name=(ApplicationStatusName, app.status.name),
        description=(str, app.description),
        url=(str, app.url),
    )
    return [
        c.Page(
            components=[
                c.Button(text="Back", on_click=BackEvent()),
                c.Heading(text=f"Edit Application for {app.employer.name}", level=2),
                c.ModelForm(
                    model=update_form,
                    display_mode="page",
                    submit_url=f"/api/application/update/{id}",
                ),
            ]
        )
    ]


def application_header(id: int, name: str):
    return [
        c.Heading(text=f"Application to {name}", level=2),
        c.LinkList(
            links=[
                c.Link(
                    components=[c.Text(text="Details")],
                    on_click=GoToEvent(url=f"/application/{id}/details"),
                    active=f"startswith:/application/{id}/details",
                ),
                c.Link(
                    components=[c.Text(text="Updates")],
                    on_click=GoToEvent(url=f"/application/{id}/updates"),
                    active=f"startswith:/application/{id}/updates",
                ),
            ],
            mode="tabs",
        ),
        c.Link(
            components=[c.Button(text="Edit", named_style="secondary")],
            on_click=GoToEvent(url=f"/application/update-form/{id}"),
        ),
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
                            submit_url=f"/api/application/delete/{id}",
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
    ]


@router.get("/{id}/details", response_model=FastUI, response_model_exclude_none=True)
def application_details(id) -> list[AnyComponent]:
    app = ApplicationAPI.get(id)

    components = [
        *application_header(id, app.employer.name),
        c.Paragraph(text=f"Created: {app.created_at}"),
        c.Paragraph(text=f"Status: {app.status.name}, updated: {app.status_updated_at}"),
        c.Paragraph(text=app.description if app.description else "No description"),
    ]

    if app.url:
        components.append(
            c.Link(
                components=[c.Text(text=app.url if app.url else "No url")],
                on_click=GoToEvent(url=app.url),
            )
        )
    if app.location_name:
        components.append(c.Paragraph(text=f"Located in: {app.location_name}"))

    if app.job_board_name:
        components.append(c.Paragraph(text=f"Applied on: {app.job_board_name}"))

    return page("Application", components)


@router.get("/{id}/updates", response_model=FastUI, response_model_exclude_none=True)
def application_updates(id) -> list[AnyComponent]:
    app = ApplicationAPI.get(id)

    components = [
        *application_header(id, app.employer.name),
        c.Paragraph(text=f"Created: {app.created_at}"),
        c.Paragraph(text=f"Status: {app.status.name}"),
        c.Paragraph(text=app.description if app.description else "No description"),
    ]

    updates = ApplicationUpdateAPI.get_all(app.id)
    if len(updates):
        for upd in updates:
            components.append(
                c.Paragraph(text=f"{pendulum.parse(upd.created_at).diff_for_humans(pendulum.now())} |"
                            f" {upd.triggerer_type.capitalize()}"
                            f" ({upd.triggerer_id:0>2d}) {upd.description}"
                            )
            )
    else:
        components.append(c.Paragraph(text="No updates"))

    return page("Application", components)


class FilterForm(BaseModel):
    status: ApplicationStatusName


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def applications(status: str | None = None) -> list[AnyComponent]:
    apps = ApplicationAPI()
    data = apps.get_all()

    data = [
        ApplicationRow(
            id=app.id,
            status=app.status.name,
            employer=app.employer.name,
            location=app.location_name,
            job_board=app.job_board_name,
            description=app.description,
            created_at=pendulum.parse(app.created_at).diff_for_humans(pendulum.now(tz=TZ)),
        )
        for app in data
    ]
    if status:
        data = [app for app in data if app.status == status]

    components = [
        c.Link(
            components=[c.Button(text="New")],
            on_click=GoToEvent(url="create-form"),
        ),
    ]

    if len(data):
        components += [
            c.ModelForm(
                model=FilterForm,
                submit_url=".",
                method="GOTO",
                submit_on_change=True,
                display_mode="inline",
            ),
            c.Table(
                data=data,
                columns=[
                    DisplayLookup(field="id", on_click=GoToEvent(url="{id}/details")),
                    DisplayLookup(field="status"),
                    DisplayLookup(field="employer"),
                    DisplayLookup(field="location"),
                    DisplayLookup(field="job_board"),
                    DisplayLookup(field="created_at", mode=DisplayMode.date),
                    DisplayLookup(field="description"),
                ],
            ),
        ]

    return page("Applications", components)
