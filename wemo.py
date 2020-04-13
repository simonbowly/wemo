#!/usr/bin/env python3
#
# Requirements:
#     - `requests` package (`pip install requests`)
#     - [Advised] static IP allocation for your WeMo devices

# client.py from https://github.com/iancmcc/ouimeaux/
#   :author: Fabio "BlackLight" Manganiello <info@fabiomanganiello.com>
# insight API from https://chameth.com/monitoring-power-with-wemo/

# Request to make
#
# POST /upnp/control/insight1 HTTP/1.1
# Accept: */*
# Accept-Encoding: gzip, deflate
# Accept-Language: en-GB,en;q=0.8
# Content-Type: text/xml
# Origin: chrome-extension://aejoelaoggembcahagimdiliamlcdmfm
# SOAPACTION: "urn:Belkin:service:insight:1#GetPower"
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.29 Safari/537.36

# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
#     <s:Body>
#         <u:GetPower xmlns:u="urn:Belkin:service:insight:1"/>
#     </s:Body>
# </s:Envelope>

# Response
#
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
#     <s:Body>
#         <u:GetPowerResponse xmlns:u="urn:Belkin:service:insight:1">
#             <InstantPower>92170</InstantPower>
#         </u:GetPowerResponse>
#     </s:Body>
# </s:Envelope>


import re
import textwrap

from xml.dom.minidom import parseString

import click
import requests


def post_basic_event(device: str, action: str, port: int = 49153, value=None):
    state = action[3:]
    value = value if value is not None else ""
    response = requests.post(
        f"http://{device}:{port}/upnp/control/basicevent1",
        headers={
            "User-Agent": "",
            "Accept": "",
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPACTION": f'"urn:Belkin:service:basicevent:1#{action}"',
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
                    <u:{action} xmlns:u="urn:Belkin:service:basicevent:1">
                        <{state}>{value}</{state}>
                    </u:{action}
                ></s:Body>
            </s:Envelope>
            """
            ),
        ),
    )
    dom = parseString(response.text)
    return dom.getElementsByTagName(state).item(0).firstChild.data


def switch_on(device: str, **kwargs):
    return post_basic_event(device=device, action="SetBinaryState", value=1, **kwargs)


def switch_off(device: str, **kwargs):
    return post_basic_event(device=device, action="SetBinaryState", value=0, **kwargs)


def is_switched_on(device: str, **kwargs):
    return bool(int(post_basic_event(device=device, action="GetBinaryState", **kwargs)))


def get_name(device: str, **kwargs):
    return post_basic_event(device=device, action="GetFriendlyName", **kwargs)


def get_device(device: str, **kwargs):
    return {
        "ip": device,
        "name": get_name(device, **kwargs),
        "switched_on": is_switched_on(device, **kwargs),
    }


@click.command()
@click.argument("device-ip")
@click.argument("command", type=click.Choice(["on", "off", "check"]))
def cli(command, device_ip):
    device = get_device(device_ip)
    if command == "check":
        click.echo(
            f"WEMO '{device['name']}' is currently switched {'on' if device['switched_on'] else 'off'}"
        )
        return
    if command == "on" and not device["switched_on"]:
        click.echo(f"Switching on WEMO '{device['name']}'")
        switch_on(device_ip)
        return
    if command == "off" and device["switched_on"]:
        click.echo(f"Switching off WEMO '{device['name']}'")
        switch_off(device_ip)
        return
    click.echo(
        f"WEMO '{device['name']}' is already switched {'on' if device['switched_on'] else 'off'}"
    )


if __name__ == "__main__":
    cli()
