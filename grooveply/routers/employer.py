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
from ..apis.employer import EmployerAPI
from ..models import ApplicationStatusName, TimePeriod
from ..settings import DB_NAME
from ..utils import page

router = APIRouter()


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def employer_page(id) -> list[AnyComponent]:
    employer_page = EmployerAPI.get_page(id)
    return page(employer_page.name, [
        c.Heading(text=employer_page.name),
        c.Paragraph(text=f"Total applications: {employer_page.total_applications}"),
        c.Paragraph(text=f"Total locations: {employer_page.total_locations}"),
    ])
