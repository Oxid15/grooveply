import os
import sys

import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import create_tables
from models import Application, ApplicationStatus, Employer

from grooveply.apis.application import ApplicationAPI

INPUT = "example.csv"

if __name__ == "__main__":
    create_tables()

    df = pd.read_csv(INPUT)

    # TODO:
    # for data in tqdm(df.itertuples(), total=len(df)):
    #     ApplicationAPI.create(
            
    #     )
