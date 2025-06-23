# setup.py
from setuptools import setup, find_packages

setup(
    name='crdc_agent',
    version='0.1',
    packages=find_packages(),  # Automatically finds 'tools' if it has __init__.py
)