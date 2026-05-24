"""Virial coefficient calculations.

This package will provide equations and calculators for the second virial
coefficient `B(T)` using fitted or predefined intermolecular potentials.
"""

from virialpy.virial.b2 import second_virial_coefficient
from virialpy.virial.mayer import mayer_function, mayer_integrand

__all__ = [
    "mayer_function",
    "mayer_integrand",
    "second_virial_coefficient",
]

