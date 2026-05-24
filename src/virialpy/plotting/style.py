"""Matplotlib style configuration for virialpy figures."""

from __future__ import annotations

import matplotlib as mpl


def set_plot_style() -> None:
    """Configure a clean scientific plotting style using Matplotlib rcParams.

    The style uses Matplotlib's built-in mathtext engine and does not require
    an external LaTeX installation.
    """
    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "figure.figsize": (6.0, 4.0),
            "figure.constrained_layout.use": False,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "mathtext.default": "regular",
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "axes.linewidth": 0.9,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "0.85",
            "grid.linestyle": "--",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 4,
            "ytick.major.size": 4,
            "xtick.minor.size": 2,
            "ytick.minor.size": 2,
            "legend.fontsize": 10,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "legend.edgecolor": "0.8",
            "lines.linewidth": 1.8,
            "lines.markersize": 5,
            "savefig.bbox": "tight",
        }
    )

