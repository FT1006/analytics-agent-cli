from setuptools import setup, find_packages

setup(
    name="analytics-agent-cli",
    version="0.1.0", 
    description="Analytics Agent CLI - AI analytics agent for data analysis and insights",
    author="FT1006",
    packages=find_packages(),
    install_requires=[
        "google-genai==1.12.1",
        "python-dotenv==1.1.0",
    ],
    entry_points={
        "console_scripts": [
            "aacli=staffer.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)