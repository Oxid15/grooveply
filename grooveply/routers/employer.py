import sqlite3
from typing import Optional

from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel

from ..apis.employer import EmployerAPI
from ..settings import DB_NAME
from ..utils import crop_text, page

router = APIRouter()


class ApplicationRow(BaseModel):
    id: int
    status: str
    location: Optional[str] = None
    job_board: Optional[str] = None
    created_at: str
    description: Optional[str] = None


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def employers() -> list[AnyComponent]:
    emps = EmployerAPI.get_all()

    cnt = EmployerAPI.get_total_count()

    components = [c.Paragraph(text=f"{cnt} Employers Total")]

    components.append(
        c.Table(
            data=emps,
            columns=[
                DisplayLookup(field="id", on_click=GoToEvent(url="/employer/{id}")),
                DisplayLookup(field="name"),
                DisplayLookup(field="application_count"),
                DisplayLookup(field="latest_apply", mode=DisplayMode.date),
            ],
        )
    )

    return page("Employers", components)


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def employer_page(id) -> list[AnyComponent]:
    employer_page = EmployerAPI.get_page(id)

    components = [
        c.Heading(text=employer_page.name),
        c.Paragraph(text=f"Created {employer_page.created_at}"),
        c.Paragraph(text=f"Total applications: {employer_page.total_applications}"),
        c.Paragraph(text=f"Total locations: {employer_page.total_locations}"),
    ]

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute(
        """
        SELECT
            a.id,
            as2.name AS status_name,
            l.name as location_name,
            jb.name as job_board_name,
            a.created_at,
            description
        FROM application a
        JOIN application_status as2 
        on a.status_id = as2.id
        left JOIN location l
        on a.location_id = l.id
        left JOIN job_board jb 
        on a.job_board_id = jb.id
        where employer_id = ?
    """,
        (id,),
    )
    data = cur.fetchall()

    data = [
        ApplicationRow(
            id=item[0],
            status=item[1],
            location=item[2],
            job_board=item[3],
            created_at=item[4],
            description=crop_text(item[5], 75),
        )
        for item in data
    ]

    table = c.Table(
        data=data,
        columns=[
            DisplayLookup(field="id", on_click=GoToEvent(url="/application/{id}/details")),
            DisplayLookup(field="status"),
            DisplayLookup(field="location"),
            DisplayLookup(field="job_board"),
            DisplayLookup(field="created_at", mode=DisplayMode.date),
            DisplayLookup(field="description"),
        ],
    )
    components.append(table)

    return page(employer_page.name, components)
