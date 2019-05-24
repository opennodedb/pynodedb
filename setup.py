from setuptools import setup, find_packages

# List of dependencies installed via `pip install -e .`
# by virtue of the Setuptools `install_requires` value below.
requires = [
    'flask',
    'flask_sqlalchemy',
    'pymysql',
    'waitress',
]

setup(
    name='pynodedb',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
