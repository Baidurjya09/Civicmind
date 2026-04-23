"""
CivicMind — Setup Script
Install as package: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="civicmind",
    version="1.0.0",
    author="Baidurjya",
    description="AI Governance Simulation Arena — Meta × HF OpenEnv Hackathon 2025",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/civicmind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "civicmind-train=training.train_grpo:main",
            "civicmind-eval=evaluate:main",
            "civicmind-api=apis.mock_apis:main",
        ],
    },
)
