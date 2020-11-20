from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [x.strip() for x in f]

setup(name='tcp_ping',
      version='1.3',
      description='Like ping, but with tcp.',
      packages=find_packages(),
      test_suite='tests',
      install_requires=requirements,
      python_requires=">=3.8",
      )
