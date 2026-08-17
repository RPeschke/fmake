from build_helpers.MD import md_concat 
import subprocess
import sys


from pathlib import Path
import shutil
import fmake


@fmake.program
def doc():
    long_description = md_concat(
        [
        "doc/why.md",
        "doc/fmake.md",
        "doc/vivado_build_project.md",
        "doc/Command-Line Bindings.md",
        ]
    )

    with open("README2.md" , "w", encoding="utf-8") as f:
        f.write(long_description)

    print("done compiling the Documentation")


@fmake.program
def build():
    doc()

    result = subprocess.run(
        [sys.executable, "-m", "build"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(
            f"Package build failed with return code {result.returncode}"
        )
    print("done building")

    
@fmake.program
def upload():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "dist/*",
            "--verbose",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
    )

    print(result.stdout)
    result.check_returncode()
    print("done uploading")


@fmake.program
def clean():
    # Remove generated PyPI README
    readme = Path("README2.md")
    if readme.exists():
        readme.unlink()

    # Remove everything in dist/ except .gitignore
    dist = Path("dist")

    if dist.exists():
        for path in dist.iterdir():
            if path.name == ".gitignore":
                continue

            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    print("done cleaning up")