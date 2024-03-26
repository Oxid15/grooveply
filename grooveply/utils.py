from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent


def page(title, components: list[AnyComponent]) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"Grooveply {title}"),
        c.Navbar(
            title="Grooveply",
            title_event=GoToEvent(url="/"),
            start_links=[
                c.Link(
                    components=[c.Text(text="Applications")],
                    on_click=GoToEvent(url="/application/"),
                    active="startswith:/application/",
                ),
                c.Link(
                    components=[c.Text(text="Automations")],
                    on_click=GoToEvent(url="/automation/"),
                    active="startswith:/automation/",
                ),
                c.Link(
                    components=[c.Text(text="Locations")],
                    on_click=GoToEvent(url="/location/"),
                    active="startswith:/location/",
                ),
                c.Link(
                    components=[c.Text(text="Job Boards")],
                    on_click=GoToEvent(url="/job_board/"),
                    active="startswith:/job_board/",
                ),
            ],
        ),
        c.Page(components=components),
    ]
