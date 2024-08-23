from setuptools import find_packages, setup

exclude_packages = []

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    reqs = [
        line.strip() for line in f if not any(pkg in line for pkg in exclude_packages)
    ]

setup(
    name="tovana",
    version="0.0.9",
    description="Memory management library to enhance AI agents with smarter, personalized, context-aware responses",
    packages=["tovana"] + ["tovana." + pkg for pkg in find_packages("memory")],
    package_dir={"tovana": "memory"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/assafelovic/tovana",
    author="Assaf Elovic",
    author_email="assaf.elovic@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    license="Apache License 2.0",
    install_requires=reqs,
)
