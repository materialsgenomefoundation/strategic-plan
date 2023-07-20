"""build tasks"""

from pathlib import Path
from shlex import split
from shutil import rmtree
from sys import executable
import appdirs
from doit.tools import create_folder


HERE = Path(__file__).parent


def rimraf(x):
    rmtree(X, True)


def do(*x):
    from doit.tools import CmdAction

    if len(x) == 1:
        x = tuple(split(*x))

    return CmdAction(list(x), shell=False)


class C:
    PY_VERSION = "3.11"
    EXE = Path(executable)


class X:
    CACHE = Path(appdirs.user_cache_dir("mgf-strategic-plan", "mgf"))
    DATA = Path(appdirs.user_data_dir("mgf-strategic-plan", "mgf"))
    CONDA = CACHE / ".conda"
    PY_EXEC = CONDA / "bin" / "python"
    TOC = HERE / "toc.yml"
    CONFIG = HERE / "config.yml"
    CONF = HERE / "conf.py"
    RUN = f"conda run --live-stream -p {CONDA}"
    PDF_BUILD = DATA / "pdf"
    TEX = DATA / "pdf" / "MGF-Strategic-Plan.tex"
    PDF = DATA / "pdf" / "MGF-Strategic-Plan.pdf"
    HTML = DATA / "html"
    CWD = Path().absolute()
    BUILD = HERE / "_build" / "html"
    PLANS = BUILD / "strategic-plan"
    STATIC = HERE / "_static"


def task_env():
    return dict(
        actions=[
            do(
                f"""conda create -y \
                    -p {X.CONDA} \
                    -c conda-forge
                    python={C.PY_VERSION} \
                    tectonic \
                    jupyter-book"""
            )
        ],
        uptodate=[X.PY_EXEC.exists],
        clean=[
            do(
                f"""conda remove -y \
                  -p {X.CONDA} --all"""
            )
        ],
    )


def task_configure():
    """build a pdf of the strategic document"""
    return dict(
        actions=[
            do(
                f"""{X.RUN} jb config sphinx \
                    --config {X.CONFIG.absolute()} \
                    --toc {X.TOC.absolute()} \
                    {HERE.absolute()}"""
            )
        ],
        verbosity=2,
        task_dep=["env"],
        targets=[X.CONF],
        file_dep=[X.TOC, X.CONFIG],
        clean=True,
    )


def task_pdf():
    """build a pdf of the strategic document"""
    yield dict(
        name="tex",
        actions=[do(f"""{X.RUN} sphinx-build -b latex {HERE} {X.PDF_BUILD}""")],
        task_dep=["logo"],
        file_dep=[X.CONF],
        targets=[X.TEX],
        clean=[(rimraf, [X.PDF_BUILD])],
    )
    yield dict(
        name="pdf",
        actions=[
            f"{X.RUN} tectonic -X compile {X.TEX}",
            f"cp {X.PDF} {X.PLANS}",
            f'echo "copied {X.PLANS / X.PDF.name}"',
        ],
        file_dep=[X.TEX],
        clean=[(rimraf, [X.PDF_BUILD]), f"rm {X.PLANS / X.PDF.name}"],
        targets=[X.PLANS / X.PDF.name],
    )


def task_html():
    """build a pdf of the strategic document"""
    return dict(
        actions=[
            do(
                f"""{X.RUN} jb build \
                    --config {X.CONFIG.absolute()} \
                    --toc {X.TOC.absolute()} \
                    {HERE.absolute()}"""
            )
        ],
        task_dep=["logo"],
        file_dep=[X.CONF],
        targets=[X.BUILD / "index.html"],
        clean=[(rimraf, [X.BUILD])],
    )


def task_logo():
    return dict(
        targets=(
            targets := [X.STATIC / f"logo-{sz}.png" for sz in [32, 128, 256, 512]]
        ),
        actions=[(create_folder, [X.STATIC])]
        + [
            do(
                f"wget -O{x} https://avatars.githubusercontent.com/u/71715171?s={sz}&v=4"
            )
            for x, sz in zip(targets, [32, 128, 256, 512])
        ],
        uptodate=[x.exists for x in targets],
    )
