"""Registry of built-in intermolecular potentials."""

from virialpy.potentials.improved_lennard_jones import improved_lennard_jones
from virialpy.potentials.lennard_jones import lennard_jones
from virialpy.potentials.rydberg import rydberg6

POTENTIALS = {
    "lj": lennard_jones,
    "ilj": improved_lennard_jones,
    "ryd6": rydberg6,
}

