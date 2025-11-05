"""
Setup configuration for ORE Supply Winrate Analyzer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ore-winrate-analyzer",
    version="1.0.0",
    author="JLBcode",
    description="基于贝叶斯推理的 ORE Supply 游戏智能分析器 - Bayesian inference-based analyzer for ORE Supply game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JLBcode-code/ore-winrate-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ore-analyzer=cli:main",
        ],
    },
    keywords="bayesian inference winrate analyzer game ore supply kelly criterion investment",
)
