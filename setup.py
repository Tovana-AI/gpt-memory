from setuptools import find_packages, setup

exclude_packages = []

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    reqs = [
        line.strip() for line in f if not any(pkg in line for pkg in exclude_packages)
    ]

setup(
    name="memory",
    version="0.0.2",
    description="Memory management system to enhance AI agents with personalized, context-aware responses",
    package_dir={"memory": "memory"},
    packages=find_packages(exclude=exclude_packages),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/assafelovic/gpt-memory",
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
