# Grooveply
Simple job application tracking app build with fastui

## Installation and usage

Clone the repo and install it with
```bash
pip install -e .
```
*(you may want to create a venv for this)*

Then run it from command line
```bash
grooveply
```

It will start the uvicorn server at `127.0.0.1:8000` which you can open with your web browser.

## Features

1. Create and track applications
2. Update statuses and descriptions
3. Set automatic status changes if certain time passed

## Stack

The web interface is built on fastui and all the data is stored in SQLite database.
