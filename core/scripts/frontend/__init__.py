#
# Frontends provide pretty ways of looking at bugs.
#
# There are 2 main (intersecting) aspects to the frontend:
# - Classes: define certain behaviours, valid fields, and custom fields
# - Bug Views: define new behaviours, features, and display formats
#

from tiqit import *

# Import our sub-modules, which do all the work
from classes import *
from views import *
