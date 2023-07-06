"""build tasks"""

from multiprocessing import active_children
from pathlib import Path
from shlex import split
from shutil import rmtree
from sys import executable
import appdirs

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
    RUN = F"conda run --live-stream -p {CONDA}"
    PDF_BUILD = DATA / "pdf"
    TEX = DATA / "pdf" / "MGF-Strategic-Plan.tex"
    PDF = DATA / "pdf" / "MGF-Strategic-Plan.pdf"
    HTML = DATA / "html"
    CWD = Path().absolute()

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
def task_pdf():
    """build a pdf of the strategic document"""
    yield dict(
        name="configure",
        actions=[do(F"""{X.RUN} jb config sphinx \
                    --config {X.CONFIG.absolute()} \
                    --toc {X.TOC.absolute()} \
                    {HERE.absolute()}""")],
        verbosity=2,
        task_dep=["env"],
        targets=[X.CONF],
        file_dep=[X.TOC, X.CONFIG],
        clean=True
    )
    yield dict(
        name="tex",
        actions=[do(F"""{X.RUN} sphinx-build -b latex {HERE} {X.PDF_BUILD}""")],
        file_dep=[X.CONF],
        targets=[X.TEX],
        clean=[(rimraf, [X.PDF_BUILD])]
    )
    yield dict(
        name="pdf",
        actions=[
            F"tectonic -X compile {X.TEX}",
            F"mv {X.PDF} {X.CWD}"
        ],
        file_dep=[X.TEX],
        targets=[X.CWD / X.PDF.name]
    )