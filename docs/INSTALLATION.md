# Installation Guide

## HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/jwpieroen/essent-ha-integration`
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

After installation, you should see 5 enabled sensors:
- `sensor.essent_electricity_current_price`
- `sensor.essent_electricity_next_price`
- `sensor.essent_electricity_average_today`
- `sensor.essent_gas_current_price`
- `sensor.essent_gas_next_price`

And 2 disabled sensors (can be enabled in entity settings):
- `sensor.essent_electricity_lowest_price_today`
- `sensor.essent_electricity_highest_price_today`
