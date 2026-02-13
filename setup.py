from setuptools import setup
from Cython.Build import cythonize
from pathlib import Path

extensions = cythonize(
    [str(p) for p in Path("src").rglob("*.pyx")],
    compiler_directives={'language_level': "3"}
)

setup(
    name='aima_toolkit',
    ext_modules=extensions,
)