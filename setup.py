import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fmake", 
    version="0.0.8",
    author="Richard Peschke",
    author_email="peschke@hawaii.edu",
    description="build scripts for firmware projects",
    long_description="long_description",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'pandas',
          'numpy',
          'matplotlib',
          'wget',
          'openpyxl',
          'uproot'
    ],
    python_requires='>=3.8',
    
    entry_points = {
        'console_scripts': ['fmake=vhdl_build_system.main_vhdl_make:main_vhdl_make'],
    }
)
