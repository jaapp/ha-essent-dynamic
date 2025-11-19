# Installation Guide

## HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/jaapp/ha-essent-dynamic`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Essent integration
9. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/essent` directory to your `config/custom_components` folder
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click "+ Add Integration"
5. Search for "Essent"
6. Click to add

## Configuration

No configuration required! The integration uses Essent's public API.

## Verification

After installation, you should see 5 enabled sensors (with entity IDs):
- Essent Dynamic Prices Electricity current price (`sensor.essent_electricity_current_price`)
- Essent Dynamic Prices Electricity next price (`sensor.essent_electricity_next_price`)
- Essent Dynamic Prices Electricity average today (`sensor.essent_electricity_average_today`)
- Essent Dynamic Prices Gas current price (`sensor.essent_gas_current_price`)
- Essent Dynamic Prices Gas next price (`sensor.essent_gas_next_price`)

And 2 disabled sensors (can be enabled in entity settings):
- Essent Dynamic Prices Electricity lowest price today (`sensor.essent_electricity_lowest_price_today`)
- Essent Dynamic Prices Electricity highest price today (`sensor.essent_electricity_highest_price_today`)

## Removal / Uninstallation

### Removing the Integration

1. Go to Settings → Devices & Services
2. Find "Essent Dynamic Prices" in the list
3. Click the three dots menu
4. Select "Delete"
5. Confirm the deletion

This will remove the integration and all its entities from Home Assistant.

### Uninstalling via HACS

If you want to completely uninstall the integration:

1. First remove the integration using the steps above
2. Open HACS → Integrations
3. Find "Essent Dynamic Prices"
4. Click the three dots menu
5. Select "Remove"
6. Restart Home Assistant

### Manual Uninstallation

If you installed manually:

1. First remove the integration from Home Assistant (see "Removing the Integration" above)
2. Delete the `config/custom_components/essent` directory
3. Restart Home Assistant
