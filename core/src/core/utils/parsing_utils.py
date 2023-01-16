from datetime import datetime

import dateutil.parser


def str_to_datetime(s) -> datetime:
    """ Parse datetime from string. """

    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return dateutil.parser.isoparse(s)
