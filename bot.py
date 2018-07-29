#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
import json
import os
from slackclient import SlackClient
import replies


try:
    SETTINGS_FILE = "example_settings.json"
    if os.path.isfile(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            SETTINGS = json.loads(f.read())
    else:
        print("Invalid '{SETTINGS_FILE}' settings file.")
        exit(0)
except:
    print("error: invalid name specified")

SLACK_CLIENT = SlackClient(SETTINGS['SLACK_BOT_TOKEN'])
BOT_NAME = SETTINGS['BOT_NAME']
NO_REPEAT_MINUTES = int(SETTINGS['NO_REPEAT_MINUTES'])


def respond(text, channel_id):
    """send response to channel"""
    message_resp = replies.GetReply().get_response(user="demo", message=text)
    response = "<@%s> %s" % (user_id, message_resp)
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel_id, text=response, as_user=True)


def get_username(user_id):
    """get username for given id"""
    api_call = SLACK_CLIENT.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('id') == user_id:
                return user.get('name')


def get_users():
    """
    Fetch a dictionary of username and their IDs from Slack
    """
    api_call = SLACK_CLIENT.api_call('users.list')
    if api_call.get('ok'):
        user_list = dict([(x['name'], x['id']) for x in api_call['members']])
        return user_list
    else:
        print 'Error Fetching Users'
        return None


def parse_slack_output(slack_rtm_firehose):
    """
    Checks slack events 'firehose' for user messages,
    returns user, message, channel
    """
    if slack_rtm_firehose and len(slack_rtm_firehose) > 0:
        for event in slack_rtm_firehose:
            if len(event) == 1:  # default first event
                print (event)
            if event and 'text' in event:
                return event['user'], event['text'].strip().lower(), event['channel']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    #
    if SLACK_CLIENT.rtm_connect(with_team_state=False):
        print('SLACK_BOT connected and running')
        bot_id = SLACK_CLIENT.api_call("auth.test")["user_id"]
        users = get_users()
        print(users)

        LAST_MESSAGE = ['', datetime.now() - timedelta(minutes=2)]

        while True:
            user_id, message, channel = parse_slack_output(SLACK_CLIENT.rtm_read())
            if user_id and message and channel:
                user_name = get_username(user_id)

                if user_id != bot_id:
                    print("{0}: {1}".format(user_name, message))
                    if message == LAST_MESSAGE[0] and \
                            LAST_MESSAGE[1] < datetime.now() + timedelta(minutes=NO_REPEAT_MINUTES):
                        print("Too soon. Skipping repeat response.")
                        pass
                    else:
                        respond(message, channel)
                        LAST_MESSAGE = [message, datetime.now()]
                else:
                    pass
            time.sleep(READ_WEBSOCKET_DELAY)

else:
    print('Connection failed. Invalid Slack token or bot ID?')