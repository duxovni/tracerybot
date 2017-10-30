# mastodon tracery bot

A mastodon bot to post procedurally-generated text at regular intervals.

The bot is written in Python 3 and uses [Tracery](https://pypi.python.org/pypi/tracery) and [Mastodon.py](https://github.com/halcy/Mastodon.py).  It's adapted from https://github.com/sipb/mastodon-bot-autoresponder .

The bot will periodically post toots generated using a provided Tracery grammar.  It will also post in response to requests from others.

# Configuration

The bot is configured in a JSON file that looks like this:

```
{
    "base_url": "https://botsin.space",
    "client_id": "0dd...65d",
    "client_secret": "a7e...6b7",
    "access_token": "9af...d33",

    "post_interval": 30,

    "state_file": "/home/mastodon/tracerybot/state"
    "grammar_file": "/home/mastodon/tracerybot/grammar.json"
}
```

All keys are mandatory.

* The first group contains information about connecting to the API and
  authenticating to it.
* The second group contains the interval in minutes to wait between
  posting new images.
* The last group contains the path to the state file, which keeps
  track of which notifications have already been read, and which
  doesn't need to exist at startup; and the grammar file, which
  contains the Tracery grammar that the bot will use to generate toots
  (see https://github.com/galaxykate/tracery for details).  This
  grammar should contain a symbol called "toot" for periodic
  unprompted toots, and a symbol called "reply" for replies.

# Installation

This should really be packaged as a proper Python package, but I haven't done that. If you want to run this bot:

```
# 1. clone this repo
git clone git@github.com:sdukhovni/tracerybot.git

# 2. set up a virtual environment for Python and activate it
virtualenv -p python3 env
source env/bin/activate

# 3. install the dependencies
pip install Mastodon.py==1.1.1
pip install beautifulsoup4==4.6.0
pip install tracery==0.1.1
pip install python-magic==0.4.13

# 4. use tokentool to register the bot as an app on your server,
# then authenticate to it (don't worry, it's not hard, there's a nice
# interactive text interface)
python tokentool.py

# 5. create a config file and edit it appropriately
cp sample_config.json config.json
nano config.json

# 6. create a tracery grammar and edit it
cp sample_grammar.json grammar.json
nano grammar.json

# 6. run the bot!
python tracerybot.py -c config.json
```
