from typing import Literal, Optional

from pydantic import BaseModel

ApplicationStatusName = Literal[
    "TO APPLY", "APPLIED", "ACTIVE", "STALE", "REJECT", "CLOSED"
]

TimePeriod = Literal["years", "months", "days"]


class ApplicationStatus(BaseModel):
    id: Optional[int] = None
    name: ApplicationStatusName = "APPLIED"


class ApplicationUpdate(BaseModel):
    id: int
    description: str
    created_at: str
    triggerer_type: str
    triggerer_id: int
    application_id: Optional[int] = None


class LatestUpdateRow(BaseModel):
    triggerer: str
    application_id: int
    employer: str
    description: str
    created_at: str


class LatestAutomationUpdateRow(BaseModel):
    application_id: int
    created_at: str


class Employer(BaseModel):
    id: int
    name: str


class EmployerPage(BaseModel):
    name: str
    created_at: str
    total_applications: int
    total_locations: int


class Location(BaseModel):
    id: int
    name: str
    created_at: str


class JobBoard(BaseModel):
    id: int
    name: str
    url: Optional[str]
    created_at: str


class Application(BaseModel):
    id: int
    employer: Employer
    status: ApplicationStatus
    location_name: Optional[str] = None
    job_board_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    status_updated_at: str
    created_at: str


class Automation(BaseModel):
    id: Optional[int] = None
    if_status_is: Optional[ApplicationStatus] = None
    change_status_to: Optional[ApplicationStatus] = None
    after: Optional[int] = None
    period: Optional[TimePeriod] = None
    created_at: Optional[str] = None
