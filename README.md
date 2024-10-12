# Grooveply
Simple job application tracker build with fastui

## Features

1. Create and track applications
2. Update statuses and descriptions
3. Set automatic status changes if certain time passed
4. Write notes and post updates on each application
5. Set goals as a number of applications per period of time
6. See latest updates on the main page

## Stack

The web interface is built on fastui and all the data is stored in SQLite database.

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
The database will be created next to the installed project.


## Stack

The web interface is built on fastui and all the data is stored in SQLite database.
