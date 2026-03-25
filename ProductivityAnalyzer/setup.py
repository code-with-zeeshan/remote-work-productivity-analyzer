# setup.py
from setuptools import find_packages, setup

setup(
    name="ProductivityAnalyzer",
    version="2.0.0",
    description="A desktop application that tracks and analyzes user activity for productivity insights.",
    author="Mohammad Zeeshan",
    author_email="zeeshansayfyebusiness@gmail.com",
    url="https://github.com/code-with-zeeshan/remote-work-productivity-analyzer",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyQt5>=5.15.10",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "pygetwindow>=0.0.9",
        "pandas>=2.2.0",
        "matplotlib>=3.8.0",
        "reportlab>=4.1.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "productivity-analyzer=main:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
