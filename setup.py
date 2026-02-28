#!/usr/bin/env python3
"""Setup script for Claude Telegram Bridge."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="claude-telegram-bridge",
    version="1.0.0",
    author="MJ",
    description="A Telegram bot that provides a bridge for running Claude in tmux sessions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mj/claude_telegram_bridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-bridge=src.main:run_bot",
        ],
    },
)
