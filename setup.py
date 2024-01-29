import os
import sys
from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 11)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Requests requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.

If you can't upgrade your Python version, you'll need to
pin to an older version of Requests (<2.28).
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count

            self.pytest_args = ["-n", str(cpu_count()), "--boxed"]
        except (ImportError, NotImplementedError):
            self.pytest_args = ["-n", "1", "--boxed"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

requires = []
test_requirements = []

with open("README.txt", "r", "utf-8") as f:
    readme = f.read()

setup(
    name="abnormal",
    version="0.1.0",
    description="The un-ORM.",
    long_description=readme,
    long_description_content_type="text/plain",
    author="David W. Barts",
    # author_email="private",
    # url="none yet",
    packages=["requests"],
    package_data={"": ["LICENSE"]},
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=requires,
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"test": PyTest},
    tests_require=test_requirements,
    # project_urls={
    #     "Documentation": "none yet",
    #     "Source": "none yet",
    # },
)
