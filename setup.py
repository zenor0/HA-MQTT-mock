from setuptools import setup, find_packages

from src.ha_mqtt_mock import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ha-mqtt-mock",
    version=__version__,
    author="zenor0",
    author_email="zenor0@outlook.com",
    description="Home Assistant MQTT设备模拟器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zenor0/HA-MQTT-mock",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "paho-mqtt>=1.6.1",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ha-mqtt-mock=ha_mqtt_mock.main:run",
        ],
    },
) 