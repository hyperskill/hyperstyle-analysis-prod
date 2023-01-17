## Stepik client

This module contains Stepik client ``StepikClient`` implementation.

### Supported requests

Implementation was based on open [API](https://stepik.org/api/docs/) provided by Stepik.

#### Usage

1. Create application in https://stepik.org/oauth2/applications/ (see [README.md](../../../README.md))
2. Set your client id and secret to environment variables `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`
3. Run [collect_data.py](../api/collect_data.py) setting platform parameter to `stepik`
