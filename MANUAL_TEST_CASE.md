# Manual verification case

Use this case in the project report to compare the paper calculation with the
Streamlit result.

## Inputs

| Quantity | Value |
| --- | ---: |
| Flow rate | 10 L/s |
| Static suction lift | 3 m |
| Static delivery head | 17 m |
| Suction-pipe length | 6 m |
| Suction-pipe diameter | 100 mm |
| Delivery-pipe length | 30 m |
| Delivery-pipe diameter | 80 mm |
| Darcy friction factor | 0.020 |
| Pump efficiency | 70% |
| Motor service factor | 1.15 |

## Expected results

| Result | Expected value |
| --- | ---: |
| Suction velocity | 1.273 m/s |
| Delivery velocity | 1.989 m/s |
| Suction friction loss | 0.099 m |
| Delivery friction loss | 1.513 m |
| Total manometric head | 21.612 m |
| Water power | 2.120 kW |
| Pump shaft power | 3.029 kW |
| Design motor power | 3.483 kW |
| Recommended motor | 4.00 kW |

## Assumptions

- Water density is 1000 kg/m³.
- Gravitational acceleration is 9.81 m/s².
- Both reservoirs are open to atmosphere.
- Velocity at the reservoir surfaces is negligible.
- Minor losses through bends, valves and fittings are not included.
