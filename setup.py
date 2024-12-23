from setuptools import setup, find_packages


with open("README.md") as f:
    long_description = f.read()

with open("PFTL/__init__.py") as f:
    version = f.readline()
    version = version.split("=")[-1].strip().replace("\"", "").replace("'", "")
    print(version)

setup(
    name="py4lab",
    version=version,
    packages=find_packages("."),
    url="https://github.com/PFTL/PythonForTheLab",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    author="Aquiles Carattino",
    author_email="aquiles@pythonforthelab.com",
    description="Code for Python for the Lab Workshop",
    long_description=long_description,
    long_description_content_type="text/markdown",
    test_suite="testsuite.testsuite",
    entry_points={
        "console_scripts": ["py4lab = PFTL.start:start"],
    },
    install_requires=[
        "pint",
        "pyqtgraph",
        "numpy",
        "PyYAML",
        "pyserial",
    ],
    extras_require={"docs": ["sphinx", "sphinx_rtd_theme", "sphinxcontrib-napoleon"]},
)
