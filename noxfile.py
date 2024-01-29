"""Nox sessions."""

import sys

import nox
from nox_poetry import Session, session

locations = "dataservice_publisher", "tests", "noxfile.py", "docs/conf.py"
nox.options.envdir = ".cache"
nox.options.reuse_existing_virtualenvs = True
package = "dataservice_publisher"
nox.options.sessions = (
    "lint",
    "mypy",
    "unit_tests",
    "integration_tests",
    "contract_tests",
)


@session(python="3.10")
def unit_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pyyaml",
        "pytest-mock",
        "pytest-aiohttp",
        "pytest-asyncio",
        "aioresponses",
    )
    session.run(
        "pytest",
        "-m unit",
        "-rfE",
        *args,
        env={"DATASERVICE_PUBLISHER_URL": "http://localhost:8000"},
    )


@session(python="3.10")
def integration_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pyyaml",
        "pytest-mock",
        "pytest-aiohttp",
        "aioresponses",
    )
    session.run(
        "pytest",
        "-m integration",
        "-rfE",
        *args,
        env={
            "DATASERVICE_PUBLISHER_URL": "http://localhost:8000",
            "SECRET_KEY": "super_secret",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "passw123",
            "FUSEKI_PASSWORD": "passw123",
            "FUSEKI_HOST": "http://fuseki",
            "FUSEKI_PORT": "8080",
            "LOGGING_LEVEL": "INFO",
        },
    )


@session(python="3.10")
def contract_tests(session: Session) -> None:
    """Run the contract_test suite."""
    args = session.posargs
    session.install(
        ".",
        "pytest",
        "pytest-docker",
        "pytest_mock",
        "aioresponses",
        "pytest-asyncio",
    )
    session.run(
        "pytest",
        "-m contract",
        "-rfE",
        *args,
        env={
            "DATASERVICE_PUBLISHER_URL": "http://localhost:8000",
            "DATASERVICE_PUBLISHER_PORT": "8080",
            "SECRET_KEY": "super_secret",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "passw123",
            "FUSEKI_PASSWORD": "passw123",
            "FUSEKI_HOST": "http://fuseki",
            "FUSEKI_PORT": "8080",
            "LOGGING_LEVEL": "INFO",
        },
    )


@session(python="3.10")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(python="3.10")
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
        "pep8-naming",
    )
    session.run("flake8", *args)


@session(python="3.10")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", f"--file={requirements}", "--output", "text")


@session(python="3.10")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or [
        "--install-types",
        "--non-interactive",
        "dataservice_publisher",
        "tests",
    ]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python="3.10")
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    session.install("xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@session(python="3.10")
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    session.install("sphinx", "sphinx_autodoc_typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@session(python="3.10")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
