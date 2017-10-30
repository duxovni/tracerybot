import argparse
import datetime
import json
import logging
import os
import os.path
import random
import sys
import time
import urllib.request

from bs4 import BeautifulSoup
import magic
from mastodon import Mastodon
import tracery
from tracery.modifiers import base_english

mime = magic.Magic(mime=True)

logging.basicConfig(level=logging.INFO)

class Config:
    def __init__(self, path):
        self.path = os.path.abspath(os.path.expanduser(path))

        with open(self.path) as f:
            self.from_dict(json.load(f))

    def from_dict(self, json):
        self.base_url = json['base_url']
        self.client_id = json['client_id']
        self.client_secret = json['client_secret']
        self.access_token = json['access_token']

        self.post_interval = json['post_interval']

        self.grammar_file = json['grammar_file']


def get_api(config):
    return Mastodon(client_id=config.client_id,
        client_secret=config.client_secret,
        api_base_url=config.base_url,
        access_token=config.access_token)


class TraceryBot:
    def __init__(self, config):
        self.config = config
        self.api = get_api(self.config)

        with open(self.config.grammar_file) as f:
            self.grammar = tracery.Grammar(json.load(f))
        self.grammar.add_modifiers(base_english)

        self.last_notification = -1

    def handle_notifications(self):
        try:
            notifications = self.api.notifications()
        except Exception as e:
            logging.error('Exception while fetching notifications: %s', e)
            return
                                                
        if isinstance(notifications, dict) and ('error' in notifications):
            raise Exception('API error: {}'.format(notifications['error']))

        if self.last_notification == -1:
            # if we've just started running, don't autorespond
            # retroactively
            if len(notifications) > 0:
                self.last_notification = int(notifications[0]['id'])
                logging.debug('Ignoring previous notifications up to %d', self.last_notification)
            else:
                self.last_notification = 0
        else:
            # reversed order to process notification in chronological order
            for notification in notifications[::-1]:
                if int(notification['id']) <= self.last_notification:
                    continue
                if notification['type'] != 'mention':
                    continue

                logging.debug('Handling notification %s', notification['id'])
                self.last_notification = int(notification['id'])

                sender = notification['status']['account']['acct']

                reply_attempts_remaining = 10
                while reply_attempts_remaining:
                    reply = '@{} {}'.format(
                        sender,
                        self.grammar.flatten("#reply#"))
                    if len(reply) <= 500:
                        break
                    reply_attempts_remaining -= 1

                if reply_attempts_remaining == 0:
                    logging.debug("Couldn't generate reply to notification %s", notification['id'])
                    return

                reply_sent = self.api.status_post(reply,
                    in_reply_to_id=notification['status']['id'])

                logging.info('Responded to status %s from %s',
                            notification['status']['id'],
                            notification['status']['account']['acct'])


    def post_toot(self):
        attempts_remaining = 10
        while attempts_remaining:
            toot = self.grammar.flatten("#toot#")
            if len(toot) <= 500:
                break
            attempts_remaining -= 1

        if attempts_remaining == 0:
            logging.debug("Couldn't generate toot")
            return

        self.api.status_post(toot, visibility='public')


    def run(self):
        countdown = 0
        while True:
            if countdown <= 0:
                self.post_toot()
                countdown = self.config.post_interval
            countdown -= 1
            self.handle_notifications()
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', help='File to load the config from.',
        default='config.json')

    args = parser.parse_args()

    config = Config(args.config)

    bot = TraceryBot(config)
    bot.run()

if __name__ == '__main__':
    main()
