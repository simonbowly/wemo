
# WEMO API Methods

Just a little control/query CLI so far:

* Get current state, load, time-on  `python wemo.py info <device_ip>`
* Switch on `python wemo.py control <device_ip> on`
* Switch off `python wemo.py control <device_ip> off`

## Devices

Testing this with a Wemo.Insight.D43 (unknown firmware version).

## Sources

* Ouimeaux library (https://github.com/iancmcc/ouimeaux), specifically:
    * `ouimeaux/device/insight.py` which gives the field order for data returned in the GetInsightParams field
    * `client.py` (contributed by BlackLight) which contains full SOAP requests for on/off switching (also use this to discover WEMO IP on local network if required)
* Some insight API information from https://chameth.com/monitoring-power-with-wemo/
* A partly correct list of services and fields from https://gist.github.com/nstarke/018cd98d862afe0a7cda17bc20f31a1e
