from typing import Literal, Optional

from pydantic import BaseModel

ApplicationStatusName = Literal[
    "TO APPLY", "APPLIED", "ACTIVE", "STALE", "REJECT", "CLOSED"
]

TimePeriod = Literal["years", "months", "days"]


class ApplicationStatus(BaseModel):
    id: Optional[int] = None
    name: ApplicationStatusName = "APPLIED"


class Employer(BaseModel):
    name: str


# TODO: think about how to adapt a model for
# doing updates and not having everythin optional
class Application(BaseModel):
    id: Optional[int] = None
    employer: Optional[Employer] = None
    status: Optional[ApplicationStatus] = None
    description: Optional[str] = None
    url: Optional[str] = None
    status_updated_at: Optional[str] = None
    created_at: Optional[str] = None


class Automation(BaseModel):
    id: Optional[int] = None
    if_status_is: Optional[ApplicationStatus] = None
    change_status_to: Optional[ApplicationStatus] = None
    after: Optional[int] = None
    period: Optional[TimePeriod] = None
    created_at: Optional[str] = None
