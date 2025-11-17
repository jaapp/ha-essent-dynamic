# Essent Home Assistant Integration

Home Assistant integration for Essent dynamic energy prices in the Netherlands.

## Features

- Real-time electricity and gas prices
- Hourly price updates
- Current, next, and average price sensors
- Min/max daily price tracking
- Full Energy Dashboard integration
- No authentication required (public API)

## Installation

See [Installation Guide](docs/INSTALLATION.md)

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
