from datetime import date
from typing import Annotated

from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

from ..apis.goal import GoalAPI
from ..models import TimePeriod
from ..utils import page

router = APIRouter()


class GoalForm(BaseModel):
    value: int = Field(gt=0)
    each: int = Field(1, gt=0)
    period: TimePeriod = "months"
    start_date: date
    end_date: date


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def create(form: Annotated[GoalForm, fastui_form(GoalForm)]):
    GoalAPI.create(form.value, form.each, form.period, str(form.start_date), str(form.end_date))
    return [c.FireEvent(event=GoToEvent(url="/goal/"))]


@router.get("/create-form", response_model=FastUI, response_model_exclude_none=True)
def create_form() -> list[AnyComponent]:
    return page(
        "New Goal",
        [
            c.Button(text="Back", on_click=BackEvent()),
            c.ModelForm(
                model=GoalForm,
                display_mode="page",
                submit_url="/api/goal/create",
            ),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def goals() -> list[AnyComponent]:
    goals = GoalAPI.get_all()
    return page(
        "Application Goals",
        [
            c.Heading(text="Application Goals"),
            c.Link(
                components=[c.Button(text="New")],
                on_click=GoToEvent(url="create-form"),
            ),
            (
                c.Table(
                    data=goals,
                    columns=[
                        DisplayLookup(field="id", on_click=GoToEvent(url="/goal/{id}")),
                        DisplayLookup(field="value"),
                        DisplayLookup(field="each"),
                        DisplayLookup(field="period"),
                        DisplayLookup(field="start_date"),
                        DisplayLookup(field="end_date"),
                    ],
                )
                if len(goals)
                else c.Paragraph(text="No goals yet")
            ),
        ],
    )
