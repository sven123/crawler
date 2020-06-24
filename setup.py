from setuptools import setup


setup(
    name="crawler",
    install_requires=open("requirements.txt").readlines(),
    packages=["crawler"],
    # entry_points={"console_scripts": ["crawl=crawler.main:main"]),
)
