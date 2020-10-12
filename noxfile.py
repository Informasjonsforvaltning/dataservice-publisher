"""Nox sessions."""
import tempfile
from typing import Any

import nox
from nox.sessions import Session

package = "dataservice_publisher"
locations = "src", "tests", "noxfile.py", "docs/conf.py"
nox.options.stop_on_first_error = True
nox.options.sessions = (
    "lint",
    "mypy",
    "pytype",
    "unit_tests",
    "integration_tests",
    "contract_tests",
)


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python="3.7")
def unit_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "pytest", "requests-mock", "pytest-mock",
    )
    session.run(
        "pytest",
        "-m unit",
        "-rA",
        *args,
        env={"DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080"},
    )


@nox.session(python="3.7")
def integration_tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session,
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "requests-mock",
        "pytest-mock",
    )
    session.run(
        "pytest",
        "-m integration",
        "-rA",
        *args,
        env={"DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080"},
    )


@nox.session(python="3.7")
def contract_tests(session: Session) -> None:
    """Run the contract_test suite."""
    args = session.posargs
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "pytest", "pytest-docker", "requests_mock", "pytest_mock"
    )
    session.run(
        "pytest",
        "-m contract",
        "-rA",
        *args,
        env={"DATASERVICE_PUBLISHER_URL": "http://dataservice-publisher:8080"},
    )


@nox.session(python="3.7")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python="3.7")
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
        "flake8-assertive",
        "pep8-naming",
    )
    session.run("flake8", *args)


@nox.session(python="3.7")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python="3.7")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python="3.7")
def pytype(session: Session) -> None:
    """Run the static type checker using pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


@nox.session(python="3.7")
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python="3.7")
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "sphinx", "sphinx_autodoc_typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session(python="3.7")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
