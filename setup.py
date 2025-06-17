from setuptools import setup, find_packages

# Define package dependencies
REQUIRES = [
    "flask>=2.0.0",
    "flask-cors>=3.0.0",
    "pydantic>=2.0.0",
    "google-adk>=1.0.0",
    "python-dotenv>=0.19.0",
    "requests>=2.26.0"
]

# Development dependencies
DEV_REQUIRES = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=4.0.0"
]

setup(
    name="multi_tool_agent",
    version="1.0.0",
    author="Noriko Kono",
    description="PlotBuddy Multi-Agent System for story generation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "plotbuddy=multi_tool_agent.api.server:main",
        ],
    }
)