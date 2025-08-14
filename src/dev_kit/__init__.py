"""
Dev Kit - A personal development toolkit for Flask applications.

This package provides utilities and tools for building Flask-based web applications
with common patterns and best practices.
"""

__version__ = "0.1.0"
__author__ = "Bahaa Shklawon"
__email__ = "bahaashklawon@gmail.com"

# Import main components for easier access
from .services import DevKit
from .exceptions import DevKitException

__all__ = ["DevKit", "DevKitException"]