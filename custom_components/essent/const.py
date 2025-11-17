"""Constants for the Essent integration."""

DOMAIN = "essent"
API_ENDPOINT = "https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/"
UPDATE_INTERVAL = 3600  # 1 hour in seconds
ATTRIBUTION = "Data provided by Essent"

# Energy types
ENERGY_TYPE_ELECTRICITY = "electricity"
ENERGY_TYPE_GAS = "gas"

# Price group types
PRICE_GROUP_MARKET = "MARKET_PRICE"
PRICE_GROUP_PURCHASING_FEE = "PURCHASING_FEE"
PRICE_GROUP_TAX = "TAX"
