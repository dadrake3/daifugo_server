from setuptools import setup

setup(
    name="daifugo",
    version="0.1",
    packages=["daifugo"],
    install_requires=["gql", "click"],
    entry_points="""
        [console_scripts]
        daifugo=daifugo.cli:cli
    """,
)
