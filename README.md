# Grooveply
Simple job application tracker build with fastui

## Installation and usage

Clone the repo, go inside and install it with
```bash
pip install .
```
*(you may want to create a venv for this)*

Then run it from command line
```bash
grooveply
```

or safer way

```bash
python -m grooveply
```

It will start the uvicorn server at `127.0.0.1:8000` which you can open with your web browser.

## Features

1. Create and track applications
  1. Application have statuses (APPLIED, ACTIVE, STALE, etc.)
  2. Locations
  3. URLs
  4. Descriptions
  5. Job Boards
2. Fill updates - text notes with a date about what's changed
3. Set automatic status changes if certain time passed

## Stack

The web interface is built on fastui and all the data is stored in SQLite database.
