import os

import setuptools

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


setuptools.setup(
    name="grooveply",
    version="0.1.0",
    description="Simple Job Application Tracking App",
    package_dir={"grooveply": os.path.join(SCRIPT_DIR, "grooveply")},
    entry_points={"console_scripts": ["grooveply = grooveply.main:main"]},
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastui==0.5.2",
        "pendulum==3.0.0",
        "fastapi==0.110.0",
        "uvicorn==0.28.1",
        "python-multipart==0.0.9",
    ],
)
