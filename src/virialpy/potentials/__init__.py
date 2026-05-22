"""Intermolecular potential models.

Future modules in this package should define reusable `U(r)` models, such as
Lennard-Jones, Morse, Buckingham, or system-specific fitted potentials.
"""

from virialpy.potentials.improved_lennard_jones import improved_lennard_jones
from virialpy.potentials.lennard_jones import lennard_jones
from virialpy.potentials.registry import POTENTIALS
from virialpy.potentials.rydberg import rydberg6

__all__ = [
    "POTENTIALS",
    "improved_lennard_jones",
    "lennard_jones",
    "rydberg6",
]

