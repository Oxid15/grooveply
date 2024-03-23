import os
import sys

import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from apis import ApplicationAPI
from db import create_tables
from models import Application, ApplicationStatus, Employer

INPUT = "example.csv"

if __name__ == "__main__":
    create_tables()

    df = pd.read_csv(INPUT)

    for data in tqdm(df.itertuples(), total=len(df)):
        app = Application(
            id=data.id,
            employer=Employer(name=data.employer),
            status=ApplicationStatus(name=data.status),
            description=data.description if pd.notna(data.description) else None,
            url=data.url if pd.notna(data.url) else None,
            created_at=data.created_at,
            status_updated_at=data.created_at
        )

        ApplicationAPI.create(app)
