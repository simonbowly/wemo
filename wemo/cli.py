from pprint import pprint

import click

from .api import get_insight_info, is_switched_on, switch_off, switch_on


@click.group()
def cli():
    """Control a WEMO insight device or get its current power usage."""
    pass


@cli.command()
@click.argument("device-ip")
def info(device_ip):
    """Get and print live data from WEMO Insight with the given IP address."""
    pprint(get_insight_info(device_ip))


@cli.command()
@click.argument("device-ip")
@click.argument("command", type=click.Choice(["on", "off"]))
def control(device_ip, command):
    """Switch the WEMO insight with the given IP address on/off."""
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
