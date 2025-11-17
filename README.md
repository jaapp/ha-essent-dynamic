<img width="2560" height="564" alt="afbeelding" src="https://github.com/user-attachments/assets/a33b7c89-e685-4eed-ab2a-b3712c57aeb1" />

# Essent Dynamic Prices - Home Assistant Integration

> ⚠️ **EXPERIMENTAL** - This integration is in early development and has not been extensively tested. Use at your own risk. Please report any issues on GitHub.

Home Assistant integration for Essent dynamic energy contract prices in the Netherlands.

**Note:** This integration is specifically for customers with an Essent dynamic pricing contract. It retrieves hourly electricity prices and daily gas prices from Essent's public API.

> **Disclaimer:** This integration is not affiliated with, endorsed by, or connected to Essent N.V. in any way. It is an independent community project that uses Essent's publicly available API.

## Features

- Real-time electricity prices (hourly) and gas prices (daily)
- Automatic updates on the hour
- Current, next, and average price sensors
- Min/max daily price tracking (electricity only)
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

| Sensor | Entity ID | Enabled by Default | Unit | Description |
|--------|-----------|-------------------|------|-------------|
| **Electricity Current Price** | `sensor.essent_electricity_current_price` | ✅ | €/kWh | Current hour's electricity price |
| **Electricity Next Price** | `sensor.essent_electricity_next_price` | ✅ | €/kWh | Next hour's electricity price |
| **Electricity Average Today** | `sensor.essent_electricity_average_today` | ✅ | €/kWh | Average electricity price for today |
| **Electricity Lowest Price Today** | `sensor.essent_electricity_lowest_price_today` | ❌ | €/kWh | Lowest electricity price today with time window |
| **Electricity Highest Price Today** | `sensor.essent_electricity_highest_price_today` | ❌ | €/kWh | Highest electricity price today with time window |
| **Gas Current Price** | `sensor.essent_gas_current_price` | ✅ | €/m³ | Current day's gas price |
| **Gas Next Price** | `sensor.essent_gas_next_price` | ✅ | €/m³ | Next day's gas price |
| **Gas Price Today** | `sensor.essent_gas_average_today` | ✅ | €/m³ | Today's gas price |

### Sensor Attributes

All current and next price sensors include detailed price component attributes from the API:

| Attribute | Description | Example Value |
|-----------|-------------|---------------|
| `price_ex_vat` | Price excluding VAT | 0.20743 |
| `vat` | VAT amount | 0.04356 |
| `market_price` | Spot market price component | 0.10285 |
| `purchasing_fee` | Supplier purchasing fee | 0.02528 |
| `tax` | Energy tax component | 0.12286 |
| `start_time` | Tariff period start time | 2025-11-17T22:00:00+01:00 |
| `end_time` | Tariff period end time | 2025-11-17T23:00:00+01:00 |

Average price sensors include:

| Attribute | Description | Example Value |
|-----------|-------------|---------------|
| `min_price` | Lowest price today | 0.21866 |
| `max_price` | Highest price today | 0.28848 |

Lowest/highest price sensors include:

| Attribute | Description | Example Value |
|-----------|-------------|---------------|
| `start` | Time window start | 2025-11-17T04:00:00+01:00 |
| `end` | Time window end | 2025-11-17T05:00:00+01:00 |

## Data Source

Prices are fetched from Essent's public API:
`https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/`

- **Electricity:** Hourly prices, updates every hour. Tomorrow's prices typically available after 13:00 CET.
- **Gas:** Daily prices, same price for entire day.

## License

MIT License
