from setuptools import setup


setup(
    name="jtimer-api",
    extras_require={
        "doc": [
            "sphinxcontrib.httpdomain",
            "sphinxcontrib.autohttp.flask",
            "sphinxcontrib.autohttp.flaskqref",
        ]
    },
)
