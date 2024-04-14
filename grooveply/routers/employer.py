from fastapi.routing import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c

from ..apis.employer import EmployerAPI
from ..utils import page

router = APIRouter()


@router.get("/{id}", response_model=FastUI, response_model_exclude_none=True)
def employer_page(id) -> list[AnyComponent]:
    employer_page = EmployerAPI.get_page(id)
    return page(employer_page.name, [
        c.Heading(text=employer_page.name),
        c.Paragraph(text=f"Created {employer_page.created_at}"),
        c.Paragraph(text=f"Total applications: {employer_page.total_applications}"),
        c.Paragraph(text=f"Total locations: {employer_page.total_locations}"),
    ])
