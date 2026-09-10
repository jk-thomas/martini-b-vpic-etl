"""
Config for the pull. Hardcoded rather than env-configurable.
See README > What I'd change

Note on the make list: the guide gives two different lists,
8 makes requirement first, then a second one later that adds Lexus.
Went with the 8-make list since it reads as the real requirement.
Check the README
"""

MAKES = ["Subaru", "Honda", "Toyota", "Nissan", "Mazda", "BMW", "Ford", "Chevrolet"]
VEHICLE_TYPE = "car"  # matches vPIC's "Passenger Car"
YEAR_START = 2010
YEAR_END = 2025

BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
DB_PATH = "/data/vpic.sqlite"

REQUEST_TIMEOUT_SECONDS = 15
