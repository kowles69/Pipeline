from setuptools import setup, find_packages

setup(
    name="GeoIndicateurs",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "datetime",
        "pandas",
        "pickle-mixin",
        "pathlib",
        "python-dotenv",
        "sqlalchemy",
        "futures",
        "geopandas",
        "openpyxl",
        "xlrd"
    ],
    python_requires=">=3.8",
    author="Besnier Jean-Baptiste ",
    author_email="jbesnier@grandlyon.com",
    description="Analyse de données géospatiales et calcul d'indicateurs",
    keywords="gis, spatial analysis, indicators",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
