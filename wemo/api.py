from xml.dom.minidom import parseString

import requests

from .core import formulate_request, parse_insight_data


def get_field(device_ip, service, field, **kwargs):
    request = formulate_request(device_ip, service, field, **kwargs)
    response = requests.post(**request)
    dom = parseString(response.text)
    return dom.getElementsByTagName(field).item(0).firstChild.data


def set_field(device_ip, service, field, value, **kwargs):
    request = formulate_request(device_ip, service, field, set_value=value, **kwargs)
    response = requests.post(**request)
    dom = parseString(response.text)
    return dom.getElementsByTagName(field).item(0).firstChild.data


def get_insight_info(device_ip):
    """Return a dictionary of live values of all the insight fields."""
    data = get_field(device_ip, service="insight", field="InsightParams")
    return parse_insight_data(data)


def switch_on(device_ip: str):
    set_field(device_ip, service="basicevent", field="BinaryState", value=1)


def switch_off(device_ip: str):
    set_field(device_ip, service="basicevent", field="BinaryState", value=0)


def is_switched_on(device_ip: str):
    data = get_field(device_ip, service="basicevent", field="BinaryState")
    return bool(int(data))
