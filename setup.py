import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vhdl_build_system", # Replace with your own username
    version="0.0.1",
    author="Richard Peschke",
    author_email="peschke@hawaii.edu",
    description="High Level Object Oriented Hardware Description Library",
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
          'openpyxl'
    ],
    python_requires='>=3.8',
    
    entry_points = {
        'console_scripts': ['hello_world=vhdl_build_system.example_script:hello_world'],
        'console_scripts': ['fmake=vhdl_build_system.main_vhdl_make:main_vhdl_make'],
    }
)
