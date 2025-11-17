"""Constants for the Essent integration."""

DOMAIN = "essent"
API_ENDPOINT = "https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/"
UPDATE_INTERVAL = 3600  # 1 hour in seconds
API_FETCH_OFFSET_SECONDS = 90  # stagger API calls to avoid hitting exact hour
ATTRIBUTION = "Data provided by Essent"

# Energy types
ENERGY_TYPE_ELECTRICITY = "electricity"
ENERGY_TYPE_GAS = "gas"

# Price group types
PRICE_GROUP_MARKET = "MARKET_PRICE"
PRICE_GROUP_PURCHASING_FEE = "PURCHASING_FEE"
PRICE_GROUP_TAX = "TAX"
