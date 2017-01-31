# TuckTuck
Better calendar integration between TickTick and Google Calendar.

![example](img/img1.jpg)

# Requirements
* One-way synchronization. Changes done via TickTick should be visible in Google Calendar and not wise versa.
* TuckTuck should check and/or create `tucktuck` calendar in Google Calendar.
* Calendar should be modifiable in order to allow usage of more than one color. TODO add link on reference
* Titles of completed events should be crossed and should contain ✔️ sign at the beginning.
* Event title should contains priority sign (if specified). One of: 🔻, 🔺, ⚫️.
* Event title should contains emoji signs if any present in projects name.
* There should be mapping between TickTick and Google Calendar colors.
* Event description should contains TickTick task id in next format @[task_id=9888f6b12214dds9f215]

# Dependencies
* python 3
* google-api-python-client
* oauth2client
* urllib2
* cookielib

# Usage
python3 tucktuck.py -u ticktick_username -p ticktick_password

# TickTick api
* https://ticktick.com/api/v2/user/signon?wc=true&remember=true
    with parameters `{'username': ticktick_username, 'password': ticktick_password}`
* https://ticktick.com/api/v2/user/signout
* https://ticktick.com/api/v2/batch/check/{size}
    ```
    {
        'checkPoint':...,
        'syncTaskBean': {...}
        ...
    }
    ```
