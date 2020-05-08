from .base import *
from config import *

DEBUG = False

try:
	from .local import *
except ImportError:
	pass
