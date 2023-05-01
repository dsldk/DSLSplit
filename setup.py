"""Setup.py for DSLLex."""
from setuptools import setup, find_packages

# List of requirements
requirements = []  # This could be retrieved from requirements.txt
# Package (minimal) configuration
setup(
    name="DSLSplit",
    version="0.2.0",
    description="A FastAPI webservices for splitting Danish compound words",
    packages=find_packages(),  # __init__.py folders search
    install_requires=requirements,
    include_package_data=True,
)
