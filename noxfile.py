"""Nox sessions."""
import sys

import nox
from nox_poetry import Session, session

locations = "src", "tests", "noxfile.py", "docs/conf.py"
nox.options.envdir = ".cache"
nox.options.reuse_existing_virtualenvs = True
package = "dataservice_publisher"
nox.options.sessions = (
    "lint",
    "mypy",
    "pytype",
    "unit_tests",
    "integration_tests",
    "contract_tests",
)


@session(python="3.9")
def unit_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pyyaml",
        "requests-mock",
        "pytest-mock",
    )
    session.run(
        "pytest",
        "-m unit",
        "-rA",
        *args,
        env={"DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080"},
    )


@session(python="3.9")
def integration_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pyyaml",
        "requests-mock",
        "pytest-mock",
    )
    session.run(
        "pytest",
        "-m integration",
        "-rA",
        *args,
        env={
            "DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080",
            "SECRET_KEY": "super_secret",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "passw123",
            "FUSEKI_PASSWORD": "passw123",
        },
    )


@session(python="3.9")
def contract_tests(session: Session) -> None:
    """Run the contract_test suite."""
    args = session.posargs
    session.install(".", "pytest", "pytest-docker", "requests_mock", "pytest_mock")
    session.run(
        "pytest",
        "-m contract",
        "-rA",
        *args,
        env={
            "DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080",
            "SECRET_KEY": "super_secret",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "passw123",
            "FUSEKI_PASSWORD": "passw123",
        },
    )


@session(python="3.9")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(python="3.9")
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


@session(python="3.9")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", f"--file={requirements}", "--output", "text")


@session(python="3.9")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or [
        "--install-types",
        "--non-interactive",
        "src",
        "tests",
    ]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python="3.9")
def pytype(session: Session) -> None:
    """Run the static type checker using pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    session.install("pytype")
    session.run("pytype", *args)


@session(python="3.9")
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    session.install("xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@session(python="3.9")
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    session.install("sphinx", "sphinx_autodoc_typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@session(python="3.9")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
