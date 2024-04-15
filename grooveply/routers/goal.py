from datetime import date
from typing import Annotated, Optional

import pendulum
from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

from ..apis.application import ApplicationAPI
from ..apis.goal import GoalAPI
from ..models import TimePeriod
from ..settings import TZ
from ..utils import page

router = APIRouter()


# TODO: check start_date < end_date
class GoalForm(BaseModel):
    value: int = Field(gt=0)
    each: int = Field(1, gt=0)
    period: TimePeriod = "months"
    start_date: date
    end_date: Optional[date] = Field(None, description="Leave empty if no end date")


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def create(form: Annotated[GoalForm, fastui_form(GoalForm)]):
    GoalAPI.create(
        form.value,
        form.each,
        form.period,
        str(form.start_date),
        str(form.end_date) if form.end_date is not None else None,
    )
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


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def goal_page(id) -> list[AnyComponent]:
    goal = GoalAPI.get(id)
    components = []

    if goal.end_date is not None and pendulum.parse(goal.end_date) < pendulum.now(tz=TZ):
        components.append(c.Paragraph(text=f"This goal expired since {goal.end_date}"))
    else:
        now = pendulum.now(tz=TZ)
        start_date = pendulum.parse(goal.start_date)

        rem_days = (now - start_date).total_days() % pendulum.Duration(
            **{goal.period: goal.each}
        ).total_days()
        latest_period_start = now - pendulum.Duration(days=rem_days)
        cnt = ApplicationAPI.count_since(str(latest_period_start))
        components.extend(
            [
                c.Heading(text=f"Goal {goal.id} is {int(round(cnt / goal.value * 100))}% complete"),
                c.Paragraph(text=f"Apply {goal.value} times in {goal.each} {goal.period}"),
                c.Paragraph(text=f"Started: {goal.start_date}"),
                c.Paragraph(text=f"{cnt}/{goal.value} since {latest_period_start}:"),
            ]
        )
        if goal.end_date is not None:
            components.append(c.Paragraph(text=f"Will end: {goal.end_date}"))

    return page(f"Goal {id}", components)
