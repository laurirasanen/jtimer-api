from setuptools import setup


setup(
    name="jtimer-api",
    install_requires={
        "doc": [
            "sphinxcontrib.httpdomain",
            "sphinxcontrib.autohttp.flask",
            "sphinxcontrib.autohttp.flaskqref",
        ]
    },
)
