import re
import textwrap
from datetime import datetime


GETINSIGHTPARAMS_FIELDS = [
    "state",
    "last_state_change",
    "on_for_seconds",
    "on_today_seconds",
    "on_total_seconds",
    "time_period",  # The period over which averages are calculated?
    "unknown",  # No clue what this field actually is?
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
            r"\s+",
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
