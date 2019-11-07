
from flask import Blueprint, request, Response, render_template, redirect, flash
from app import log
import requests

groupme = Blueprint('groupme', __name__)

@groupme.route("/groupme/testbot", methods=['POST'])
def testbot():
    log.info('Groupme received the following args: {}'.format(request.args))
    log.info('Sending response...')
    r = requests.post('https://api.groupme.com/v3/bots/post', params={"text" : "Hello there!", "bot_id" : "9d8e84f1d16b3275ee6da38976"})
    log.info('got repsonse: {}'.format(r))
    return Response('Received and sent a message!')
    