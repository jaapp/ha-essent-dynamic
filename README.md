# Essent Dynamic Prices - Home Assistant Integration

> ⚠️ **EXPERIMENTAL** - This integration is in early development and has not been extensively tested. Use at your own risk. Please report any issues on GitHub.

Home Assistant integration for Essent dynamic energy contract prices in the Netherlands.

**Note:** This integration is specifically for customers with an Essent dynamic pricing contract. It retrieves hourly electricity and gas prices from Essent's public API.

## Features

- Real-time electricity and gas prices
- Hourly price updates
- Current, next, and average price sensors
- Min/max daily price tracking
- Full Energy Dashboard integration
- No authentication required (public API)

## Installation

### Via HACS (Recommended)

1. Click this button:

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jaapp&repository=ha-essent-dynamic&category=integration)

Or manually:

1. Open **HACS → Integrations → Custom repositories**
2. Add `https://github.com/jaapp/ha-essent-dynamic` as an *Integration*
3. Install **Essent Dynamic Prices** and restart Home Assistant

### Manual Installation

See [Installation Guide](docs/INSTALLATION.md) for manual installation instructions.

## Energy Dashboard Setup

See [Energy Dashboard Guide](docs/ENERGY_DASHBOARD.md)

## Sensors

### Enabled by Default

- **Current Price** (electricity/gas): Current hour's energy price
- **Next Price** (electricity/gas): Next hour's energy price
- **Average Today** (electricity/gas): Average price for current day

### Disabled by Default

- **Lowest Price Today** (electricity/gas): Minimum price with time window
- **Highest Price Today** (electricity/gas): Maximum price with time window

## Price Components

Each price sensor includes detailed attributes:
- `price_ex_vat`: Price excluding VAT
- `vat`: VAT amount
- `market_price`: Spot market price component
- `purchasing_fee`: Supplier purchasing fee
- `tax`: Energy tax component

## Energy Dashboard Integration

Current price sensors include `prices_today` and `prices_tomorrow` attributes with hourly price data formatted for Home Assistant Energy Dashboard.

## Data Source

Prices are fetched from Essent's public API:
`https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/`

Data updates hourly. Tomorrow's prices typically available after 13:00 CET.

## License

MIT License
