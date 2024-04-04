from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lodash",
    version="0.0.1",
    author="Alex Osypenko",
    author_email="a.osipenko@ability.ai",
    description="llm_agency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Abilityai/lodash",
    packages=find_packages(),
    install_requires=[
        "colorist==1.6.0",
        "tiktoken",
        "langdetect==1.0.9",
        "python-iso639==2023.6.15",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)
