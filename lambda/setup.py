from setuptools import setup

setup(
    name="daifugo",
    version="0.1",
    packages=["daifugo"],
    entry_points="""
        [console_scripts]
        daifugo=daifugo.cli:cli
    """,
)
