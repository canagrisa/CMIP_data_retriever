from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip() and not line.startswith("#")]

install_requires = parse_requirements("requirements.txt")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="CMIP_data_retriever",
    version="0.1.0",
    author="Pere Rosselló",
    author_email="canagrisablog@gmail.com",
    description="A Python package to simplify downloading climate data from the CMIP6 project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/canagrisa/CMIP_data_retriever",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires = parse_requirements("requirements.txt"),
    include_package_data=True,
)
