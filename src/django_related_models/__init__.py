"""Package docstring"""

__author__ = 'Marius Mucenicu <marius_mucenicu@rover.com>'
__version__ = '0.1.0'

__all__ = [
    'RelatedModels',
    'get_related_objects',
    'get_related_objects_mapping',
]

from .related_models import get_related_objects
from .related_models import get_related_objects_mapping
from .related_models import RelatedModels
