"""Publication-quality matplotlib styling and palette helpers.

Copied into src/utils/viz.py by /init-research. Do not edit the source under
.claude/templates/ — that is the orchestrator template. To customize for a
specific project, edit the copy under src/utils/.

Design choices encoded here:
- One color is reserved for "highlight" (Okabe-Ito vermillion); the rest are
  categorical and colorblind-safe.
- Spines: only bottom and left, thin. Removes top/right chartjunk.
- Tick density limited; minor ticks off by default.
- Default figure sizes match common single-column / double-column journal
  widths (in inches).
- Save helper writes both PDF (vector, for the manuscript) and PNG@300dpi
  (for previews and Slack/Notion embeds), plus optional SVG.
- A discipline check raises if a figure has no title-or-suptitle AND no
  caller-supplied caption argument — silent untitled figures are a smell.

Usage:

    from utils.viz import apply_publication_style, save_figure, OKABE_ITO

    apply_publication_style()
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(xs, ys, color=OKABE_ITO["blue"])
    ax.set(xlabel="time (s)", ylabel="response (a.u.)")
    save_figure(fig, "data/results/<run_id>/figures/fig1", caption="...")
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Literal

import matplotlib as mpl
import matplotlib.pyplot as plt

# --- Colorblind-safe palettes ------------------------------------------------
# Okabe & Ito (2008) — eight distinguishable colors for protan/deutan/tritan.
# https://jfly.uni-koeln.de/color/
OKABE_ITO: dict[str, str] = {
    "black": "#000000",
    "orange": "#E69F00",
    "skyblue": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",   # reserved for highlight / odd-one-out
    "purple": "#CC79A7",
}
OKABE_ITO_CYCLE: list[str] = [
    OKABE_ITO["blue"],
    OKABE_ITO["vermillion"],
    OKABE_ITO["green"],
    OKABE_ITO["orange"],
    OKABE_ITO["skyblue"],
    OKABE_ITO["purple"],
    OKABE_ITO["yellow"],
    OKABE_ITO["black"],
]

# Tableau colorblind 10 — alternative when Okabe-Ito feels too saturated.
TABLEAU_CB10: list[str] = [
    "#006BA4", "#FF800E", "#ABABAB", "#595959", "#5F9ED1",
    "#C85200", "#898989", "#A2C8EC", "#FFBC79", "#CFCFCF",
]

# --- Standard journal column widths (inches) ---------------------------------
COLUMN_WIDTH = 3.5      # Single-column figure (most journals)
TWO_THIRDS_WIDTH = 5.0  # 1.5-column / Nature half-page
DOUBLE_WIDTH = 7.2      # Double-column figure
SLIDE_WIDTH = 6.0       # 16:9 slide column


# --- Style application -------------------------------------------------------
def _base_rcparams(palette: list[str]) -> dict:
    return {
        "axes.prop_cycle": mpl.cycler(color=palette),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.linewidth": 0.8,
        "axes.titlesize": "medium",
        "axes.titleweight": "regular",
        "axes.labelsize": "small",
        "axes.grid": False,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "legend.frameon": False,
        "legend.fontsize": "small",
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,   # TrueType — keeps text editable in vector editors
        "ps.fonttype": 42,
        "image.cmap": "viridis",
    }


def apply_publication_style(palette: list[str] | None = None) -> None:
    """Apply small-but-clean styling suitable for journal figures.

    Uses the generic ``serif`` family with a long fallback chain so the
    figure renders predictably across macOS / Linux / Windows. Font sizes
    are intentionally small because journal figures are reproduced at the
    size you save them. To customize, edit this file or override
    ``mpl.rcParams`` after calling this function.
    """
    rc = _base_rcparams(palette or OKABE_ITO_CYCLE)
    rc.update({
        "font.family": "serif",
        "font.serif": [
            "DejaVu Serif", "Liberation Serif", "Nimbus Roman",
            "Times New Roman", "Times", "serif",
        ],
        "font.size": 8.5,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "lines.linewidth": 1.2,
        "lines.markersize": 4.0,
    })
    mpl.rcParams.update(rc)


def apply_presentation_style(palette: list[str] | None = None) -> None:
    """Apply larger, sans-serif styling for slides and posters."""
    rc = _base_rcparams(palette or OKABE_ITO_CYCLE)
    rc.update({
        "font.family": "sans-serif",
        "font.sans-serif": [
            "DejaVu Sans", "Liberation Sans", "Helvetica", "Arial", "sans-serif",
        ],
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "axes.linewidth": 1.4,
        "xtick.major.width": 1.4,
        "ytick.major.width": 1.4,
        "xtick.major.size": 5,
        "ytick.major.size": 5,
        "lines.linewidth": 2.4,
        "lines.markersize": 7.0,
    })
    mpl.rcParams.update(rc)


# --- Save helper -------------------------------------------------------------
def save_figure(
    fig: plt.Figure,
    path_without_ext: str | Path,
    *,
    formats: Iterable[Literal["pdf", "png", "svg"]] = ("pdf", "png"),
    caption: str | None = None,
    require_caption_or_title: bool = True,
) -> list[Path]:
    """Save a figure to multiple formats with consistent settings.

    Writes a sidecar `<name>.caption.txt` if `caption` is provided, so the
    paper-writer agent can grep for figure captions later.

    Raises if the figure has no title and no caption argument and
    `require_caption_or_title` is True. Silent untitled figures are a smell.
    """
    path_without_ext = Path(path_without_ext)
    path_without_ext.parent.mkdir(parents=True, exist_ok=True)

    if require_caption_or_title and caption is None:
        has_title = bool(fig._suptitle and fig._suptitle.get_text().strip())
        if not has_title:
            for ax in fig.get_axes():
                t = ax.get_title()
                if t and t.strip():
                    has_title = True
                    break
        if not has_title:
            raise ValueError(
                f"save_figure({path_without_ext}): figure has no title and no caption "
                "argument. Pass caption='...' or set a title; or pass "
                "require_caption_or_title=False to override (not recommended)."
            )

    written: list[Path] = []
    for fmt in formats:
        out = path_without_ext.with_suffix(f".{fmt}")
        fig.savefig(out, format=fmt)
        written.append(out)

    if caption is not None:
        cap_path = path_without_ext.with_suffix(".caption.txt")
        cap_path.write_text(caption.strip() + "\n", encoding="utf-8")
        written.append(cap_path)

    return written


# --- Convenience -------------------------------------------------------------
def remove_chartjunk(ax: plt.Axes, *, keep_grid: bool = False) -> plt.Axes:
    """Idempotent cleanup for an axes that was set up by another library."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if not keep_grid:
        ax.grid(False)
    ax.tick_params(which="minor", bottom=False, left=False, top=False, right=False)
    return ax


def add_panel_label(ax: plt.Axes, label: str, *, x: float = -0.18, y: float = 1.02) -> None:
    """Add a bold (a), (b), ... panel label in axes-relative coordinates."""
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=mpl.rcParams["axes.titlesize"], fontweight="bold",
            va="bottom", ha="left")
