from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="satellite-roof-detection",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="卫星图像分割检测系统 - 基于YOLOv8的屋顶、农田检测",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/satellite-roof-detection",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
        ],
        "gpu": [
            "torch>=1.9.0+cu111",
            "torchvision>=0.10.0+cu111",
        ],
    },
    entry_points={
        "console_scripts": [
            "roof-detect-train=src.models.train:main",
            "roof-detect-predict=src.models.predict:main",
            "roof-detect-evaluate=src.models.evaluate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
)
