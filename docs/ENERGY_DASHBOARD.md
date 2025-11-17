# Energy Dashboard Integration

The Essent integration provides full support for Home Assistant's Energy Dashboard.

## Setup

### 1. Add Energy Source

1. Go to Settings → Dashboards → Energy
2. Click "Add Consumption" under Electricity or Gas grid consumption
3. Select your energy meter entity
4. Under "Use an entity with current price":
   - For electricity: Select `sensor.essent_electricity_current_price`
   - For gas: Select `sensor.essent_gas_current_price`
5. Save

### 2. Price Data

The current price sensors automatically provide:
- **Current hour price**: Used for real-time cost calculation
- **Today's hourly prices**: Available via `prices_today` attribute
- **Tomorrow's prices**: Available via `prices_tomorrow` attribute (after ~13:00 CET)

### 3. Historical Cost Tracking

The Energy Dashboard will automatically:
- Track hourly energy costs
- Display daily/monthly/yearly cost breakdowns
- Show cost trends over time
- Compare current vs historical prices

## Advanced Usage

### Creating Automations

Use price sensors to optimize energy consumption:

```yaml
automation:
  - alias: "Charge battery when cheap"
    trigger:
      - platform: numeric_state
        entity_id: sensor.essent_electricity_current_price
        below: 0.20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
```

### Template Sensors

Calculate custom metrics:

```yaml
template:
  - sensor:
      - name: "Price vs Average"
        unit_of_measurement: "%"
        state: >
          {% set current = states('sensor.essent_electricity_current_price') | float %}
          {% set avg = states('sensor.essent_electricity_average_today') | float %}
          {{ ((current - avg) / avg * 100) | round(1) }}
```

## Troubleshooting

### Prices not showing in Energy Dashboard

1. Verify sensors are available and have values
2. Check sensor state class is `measurement`
3. Ensure unit of measurement is `EUR/kWh` or `EUR/m³`
4. Restart Home Assistant

### Tomorrow's prices missing

Tomorrow's prices are published around 13:00 CET each day. Before this time, the `prices_tomorrow` attribute will be empty or missing. This is normal behavior.
