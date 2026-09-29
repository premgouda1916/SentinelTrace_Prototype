# Importing the API module creates the synthetic schema/data if needed.
from app import seed_if_empty
seed_if_empty()
print('Synthetic SentinelTrace demo data ready.')
