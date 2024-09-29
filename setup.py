from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web_content_processor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for web scraping, link extraction, and content postprocessing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/web_content_processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiofiles>=0.8.0",
        "asyncio>=3.4.3",
        "beautifulsoup4>=4.9.3",
        "gradio>=3.23.0",
        "pandas>=1.3.3",
        "playwright>=1.17.2",
        "PyYAML>=5.4.1",
    ],
    entry_points={
        "console_scripts": [
            "web_content_processor=src.integrated_app:main",
        ],
    },
)