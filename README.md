# Ninite-Helper
This app aims to fill in some gaps left by the Ninite Pro web interface,
such as the lack of an API from which to fetch reports.

By scheduling or scripting this app, you could automate the process of
running reports on a regular schedule, or install the agent silently in the background
without needing to first log in and download the agent installer.


Requirements are pretty simple:
1. You'll need Python 3.x
2. Run `pip install -r requirements.txt` to get selenium, which is the only external Python library required.
3. Install the latest version of Firefox
4. You'll need a Ninite Pro account, otherwise this app won't do much for you. You can sign up for a free two week trial here: https://ninite.com/request_trial

This is a command-line app with the following switches:

Required:

email       (Your Ninite login email)

password    (Your Ninite login password)


Optional:

-r, --reports    (Download .csv reports from the Apps and Machine Details views of the Pro web interface)

-i, --install    (Download and install the Ninite agent .msi (requires you to be on Windows as Ninite is Windows-only))

