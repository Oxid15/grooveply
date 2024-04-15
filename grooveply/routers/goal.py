from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent, PageEvent

from ..apis.goal import GoalAPI
from ..utils import page

router = APIRouter()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def goals() -> list[AnyComponent]:
    goals = GoalAPI.get_all()
    return page(
        "Application Goals",
        [
            c.Heading(text="Application Goals"),
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
            ) if len(goals) else c.Paragraph(text="No goals yet"),
        ],
    )
