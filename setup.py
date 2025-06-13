from setuptools import setup, find_packages

setup(
    name="multi_tool_agent",
    version="1.0.0",
    author="Noriko Kono",
    description="PlotBuddy Multi-Agent System for story generation",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "pydantic>=2.0.0",
        "google-adk>=1.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
    ]
)