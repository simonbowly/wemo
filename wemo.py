import re
import textwrap
from xml.dom.minidom import parseString
from datetime import datetime
from pprint import pprint

import click
import requests


GETINSIGHTPARAMS_FIELDS = [
    "state",
    "last_state_change",
    "on_for_seconds",
    "on_today_seconds",
    "on_total_seconds",
    "time_period",  # The period over which averages are calculated?
    "unknown",
    "current_power_mw",
    "today_mw",
    "total_mw",
    "power_threshold_mw",
]

INSIGHT_STATES = {
    0: "off",
    1: "on",
    8: "standby",
}


def parse_insight_data(data):
    data = dict(zip(GETINSIGHTPARAMS_FIELDS, data.split("|")))
    data = {
        k: float(v)
        if k == "total_mw"
        else datetime.fromtimestamp(int(v))
        if k == "last_state_change"
        else INSIGHT_STATES[int(v)]
        if k == "state"
        else int(v)
        for k, v in data.items()
    }
    return data


def formulate_request(host, service, field, set_value=None, port=49153):
    if set_value is None:
        action = f"Get{field}"
        value_tag = ""
    else:
        action = f"Set{field}"
        value_tag = f"<{field}>{set_value}</{field}>"
    return dict(
        url=f"http://{host}:{port}/upnp/control/{service}1",
        headers={
            "User-Agent": "",
            "Accept": "",
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPACTION": f'"urn:Belkin:service:{service}:1#{action}"',
        },
        data=re.sub(
            "\s+",
            " ",
            textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="utf-8"?>
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                        s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <s:Body>
                        <u:{action} xmlns:u="urn:Belkin:service:{service}:1">
                            {value_tag}
                        </u:{action}>
                    </s:Body>
                </s:Envelope>
                """
            ),
        ),
    )


def get_field(device_ip, service, field, **kwargs):
    # @todo Add an async API for all requests using aiohttp
    # @body Extract common request formulation and parsing, replace requests
    # with an aiohttp client.
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
    data = get_field(device_ip, service="insight", field="InsightParams")
    return parse_insight_data(data)


def switch_on(device_ip: str):
    set_field(device_ip, service="basicevent", field="BinaryState", value=1)


def switch_off(device_ip: str):
    set_field(device_ip, service="basicevent", field="BinaryState", value=0)


def is_switched_on(device_ip: str):
    return bool(int(get_field(device_ip, service="basicevent", field="BinaryState")))


@click.group()
def cli():
    pass


@cli.command()
@click.argument("device-ip")
def info(device_ip):
    pprint(get_insight_info(device_ip))


@cli.command()
@click.argument("device-ip")
@click.argument("command", type=click.Choice(["on", "off"]))
def control(device_ip, command):
    switched_on = is_switched_on(device_ip)
    if command == "on" and not switched_on:
        click.echo(f"Switching on wemo@{device_ip}")
        switch_on(device_ip)
        return
    if command == "off" and switched_on:
        click.echo(f"Switching off wemo@{device_ip}")
        switch_off(device_ip)
        return
    click.echo(f"wemo@{device_ip} is already switched {'on' if switched_on else 'off'}")


if __name__ == "__main__":
    cli()
