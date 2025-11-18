#!/usr/bin/env python3
"""
中文医学知识图谱 - Python包安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# 读取requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.startswith('#')
    ]

# 添加API依赖
api_requirements = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
]

setup(
    name="chinese-medical-kg",
    version="1.0.0",
    author="Chinese Medical KG Team",
    author_email="wang-hao@shu.edu.cn",
    description="简单、准确、开箱即用的中文医学本体标准化系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hint-lab/chinese-medical-kg",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "api": api_requirements,
        "all": requirements + api_requirements,
    },
    entry_points={
        "console_scripts": [
            "medical-kg=scripts.kg_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["ontology/data/*.db", "ontology/data/*.json"],
    },
    zip_safe=False,
)
