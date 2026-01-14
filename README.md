<img width="2560" height="564" alt="afbeelding" src="https://github.com/user-attachments/assets/a33b7c89-e685-4eed-ab2a-b3712c57aeb1" />

# ⚠️ ARCHIVED - This Repository is No Longer Maintained

**This integration is now part of the official Home Assistant core repository.**

For the most up-to-date version, documentation, and support, please refer to:
- **Official Documentation:** [Home Assistant Essent Integration](https://www.home-assistant.io/integrations/essent/)
- **Core Repository:** [home-assistant/core](https://github.com/home-assistant/core)
- **Issue Reporting:** Use the official [Home Assistant issue tracker](https://github.com/home-assistant/core/issues)

---

# Essent Dynamic Prices - Home Assistant Integration

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

### Official Home Assistant Integration (Recommended)

This integration is now built into Home Assistant. No custom installation required!

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Essent**
4. Follow the setup instructions

### Legacy Installation (This Archived Repository)

⚠️ **Not recommended** - Use the official core integration instead.

<details>
<summary>Click to expand legacy installation instructions</summary>

#### Via HACS

1. Click this button:

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jaapp&repository=ha-essent-dynamic&category=integration)

Or manually:

1. Open **HACS → Integrations → Custom repositories**
2. Add `https://github.com/jaapp/ha-essent-dynamic` as an *Integration*
3. Install **Essent Dynamic Prices** and restart Home Assistant

#### Manual Installation

See [Installation Guide](docs/INSTALLATION.md) for manual installation instructions.

</details>

## Energy Dashboard Setup

See [Energy Dashboard Guide](docs/ENERGY_DASHBOARD.md)

## Sensors

| Sensor | Entity ID | Enabled by Default | Unit | Description |
|--------|-----------|-------------------|------|-------------|
| **Essent Dynamic Prices Electricity current price** | `sensor.essent_electricity_current_price` | ✅ | €/kWh | Current hour's electricity price |
| **Essent Dynamic Prices Electricity next price** | `sensor.essent_electricity_next_price` | ✅ | €/kWh | Next hour's electricity price |
| **Essent Dynamic Prices Electricity average today** | `sensor.essent_electricity_average_today` | ✅ | €/kWh | Average electricity price for today |
| **Essent Dynamic Prices Electricity lowest price today** | `sensor.essent_electricity_lowest_price_today` | ❌ | €/kWh | Lowest electricity price today with time window |
| **Essent Dynamic Prices Electricity highest price today** | `sensor.essent_electricity_highest_price_today` | ❌ | €/kWh | Highest electricity price today with time window |
| **Essent Dynamic Prices Gas current price** | `sensor.essent_gas_current_price` | ✅ | €/m³ | Current day's gas price |
| **Essent Dynamic Prices Gas next price** | `sensor.essent_gas_next_price` | ✅ | €/m³ | Next day's gas price |

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

- **Electricity:** Hourly prices, updates every hour. Tomorrow's prices available after 12:00 CET.
- **Gas:** Daily prices, same price for entire day. Tomorrow's price available after 19:00 CET.

## Data Updates

The integration updates data in two ways:

### API Data Fetching
- **Frequency:** Once per hour at a random minute offset (0-59 minutes) - this offset is set once at setup and stays consistent
- **Single API endpoint:** Fetches both electricity and gas prices from the same API call
- **Tomorrow's data:** Automatically included in the response when available from Essent (typically after 12:00 CET for electricity, 19:00 CET for gas)
- **Resilience:** If an API fetch fails, the coordinator automatically retries at the next scheduled hourly interval

## Getting Help

For the official core integration:
- **Documentation:** [Home Assistant Essent Integration](https://www.home-assistant.io/integrations/essent/)
- **Issues:** [Home Assistant Core Issues](https://github.com/home-assistant/core/issues)
- **Community:** [Home Assistant Community Forum](https://community.home-assistant.io/)

For this archived repository:
- [Archived GitHub issues](https://github.com/jaapp/ha-essent-dynamic/issues) (read-only)

## License

MIT License
