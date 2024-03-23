from typing import Annotated, Optional

import pendulum
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastui.forms import Textarea, fastui_form
from pydantic import BaseModel, Field, create_model

from ..apis import ApplicationAPI
from ..models import Application, ApplicationStatus, ApplicationStatusName, Employer
from ..settings import TZ
from ..utils import page


class ApplicationForm(BaseModel):
    employer_name: str
    app_status_name: ApplicationStatusName = "APPLIED"
    description: Annotated[str | None, Textarea(rows=5)] = Field(None)
    url: str = None


class ApplicationUpdateForm(BaseModel):
    app_status_name: ApplicationStatusName
    description: Annotated[str | None, Textarea(rows=5)] = Field(None)
    url: str = None


class ApplicationRow(BaseModel):
    id: int
    status: str
    employer: str
    description: Optional[str] = None
    created_at: str


router = APIRouter()


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def application_create(form: Annotated[ApplicationForm, fastui_form(ApplicationForm)]):
    a = Application(
        employer=Employer(name=form.employer_name),
        status=ApplicationStatus(name=form.app_status_name),
        description=form.description,
        url=form.url,
        created_at=str(pendulum.now(tz=TZ)),
        status_updated_at=str(pendulum.now(tz=TZ)),
    )
    ApplicationAPI.create(a)
    return [c.FireEvent(event=GoToEvent(url="/application/"))]


@router.post("/update/{id}", response_model=FastUI, response_model_exclude_none=True)
def application_update(
    id, form: Annotated[ApplicationUpdateForm, fastui_form(ApplicationUpdateForm)]
):
    app = ApplicationAPI.get(id)
    if form.app_status_name != app.status.name:
        status_updated_at = str(pendulum.now(tz=TZ))
    else:
        status_updated_at = None

    a = Application(
        status=ApplicationStatus(name=form.app_status_name),
        description=form.description,
        url=form.url,
        status_updated_at=status_updated_at,
    )
    ApplicationAPI.update(id, a)
    return [c.FireEvent(event=GoToEvent(url="/application/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def application_create_form() -> list[AnyComponent]:
    return page(
        "New Application",
        [
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
                c.Heading(text=f"Edit Application for {app.employer.name}", level=2),
                c.ModelForm(
                    model=update_form,
                    display_mode="page",
                    submit_url=f"/api/application/update/{id}",
                ),
            ]
        )
    ]


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def application_get(id) -> list[AnyComponent]:
    app = ApplicationAPI.get(id)
    return page(
        "Application",
        [
            c.Heading(text=f"Application to {app.employer.name}", level=2),
            c.Button(text="Back", on_click=BackEvent()),
            c.Link(
                components=[c.Button(text="Edit", named_style="warning")],
                on_click=GoToEvent(url=f"/application/update-form/{id}"),
            ),
            c.Paragraph(text=f"Created: {app.created_at}"),
            c.Paragraph(text=f"Status: {app.status.name}, updated: {app.status_updated_at}"),
            c.Paragraph(text=app.description if app.description else "No description"),
            c.Link(
                components=[c.Text(text=app.url if app.url else "No url")],
                on_click=GoToEvent(url=app.url),
            ),
        ],
    )


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
                    DisplayLookup(field="id", on_click=GoToEvent(url="{id}")),
                    DisplayLookup(field="status"),
                    DisplayLookup(field="employer"),
                    DisplayLookup(field="created_at"),
                    DisplayLookup(field="description"),
                ],
            ),
        ]

    return page("Applications", components)
