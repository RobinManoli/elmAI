# to compile this:
# first open vscode by entering "Developer Command Prompt for VS 2019" and then type "code ."
# python cython-setup.py build_ext --inplace


from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("elmaphys.pyx")
)