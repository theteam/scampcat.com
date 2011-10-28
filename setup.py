from setuptools import setup, find_packages

setup(
    name = "scampcat",
    version = "0.2",
    url = 'http://github.com/theteam/scampcat.com',
    license = 'MIT license',
    description = 'source of scampcat.com',
    author = 'theTeam',
    packages = find_packages('.'),
    package_dir = {'': '.'},
    install_requires = ['setuptools'],
)
