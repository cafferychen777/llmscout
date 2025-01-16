from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="llmscout",
    version="0.1.0",
    author="Caffery Yang",
    author_email="cafferychen777@gmail.com",
    description="An LLM-powered tool for discovering and analyzing research papers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cafferychen777/llmscout",
    packages=find_packages(include=["llmscout", "llmscout.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "llmscout=llmscout.cli:main",
        ],
    },
)