from xml.dom.minidom import parseString

import aiohttp

from .core import formulate_request, parse_insight_data


async def get_field(device_ip, service, field, **kwargs):
    request = formulate_request(device_ip, service, field, **kwargs)
    async with aiohttp.ClientSession() as session:
        async with session.post(**request) as response:
            dom = parseString(await response.text())
            return dom.getElementsByTagName(field).item(0).firstChild.data


async def set_field(device_ip, service, field, value, **kwargs):
    request = formulate_request(device_ip, service, field, set_value=value, **kwargs)
    async with aiohttp.ClientSession() as session:
        async with session.post(**request) as response:
            dom = parseString(await response.text())
            return dom.getElementsByTagName(field).item(0).firstChild.data


async def get_insight_info(device_ip):
    """Return a dictionary of live values of all the insight fields."""
    data = await get_field(device_ip, service="insight", field="InsightParams")
    return parse_insight_data(data)


async def switch_on(device_ip: str):
    await set_field(device_ip, service="basicevent", field="BinaryState", value=1)


async def switch_off(device_ip: str):
    await set_field(device_ip, service="basicevent", field="BinaryState", value=0)


async def is_switched_on(device_ip: str):
    data = await get_field(device_ip, service="basicevent", field="BinaryState")
    return bool(int(data))
