from .health import health_bp
from .test import test_bp
from .version import version_bp  # Add this line

__all__ = ['health_bp', 'test_bp', 'version_bp']  # Add version_bp here

