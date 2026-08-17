import setuptools


from pathlib import Path
ROOT = Path(__file__).resolve().parent
long_description = (ROOT / "README2.md").read_text(encoding="utf-8")




setuptools.setup(
    name="fmake", 
    version="0.3.7",
    author="Richard Peschke",
    author_email="peschke@hawaii.edu",
    description="build scripts for firmware projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    data_files=[
        ("", ["README.md", "README2.md"]),
    ],
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
