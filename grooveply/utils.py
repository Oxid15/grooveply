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
            ],
        ),
        c.Page(components=components),
    ]
