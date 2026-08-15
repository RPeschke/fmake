import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fmake", 
    version="0.3.2",
    author="Richard Peschke",
    author_email="peschke@hawaii.edu",
    description="build scripts for firmware projects",
    long_description=long_description,
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
          "dataframe_helpers",
          "watchdog",
          "debugpy",
          "cocotb_test"
        
    ],
    python_requires='>=3.8',
    
    entry_points = {
        'console_scripts': ['fmake=fmake.fmake_main:fmake_main'],
    }
)
