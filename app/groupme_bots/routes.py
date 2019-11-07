
from flask import Blueprint, request, Response, render_template, redirect, flash
from app import log
import random
import requests

groupme = Blueprint('groupme', __name__)

@groupme.route("/groupme/testbot", methods=['POST'])
def testbot():
    log.info('Groupme received the following args: {}'.format(request.args.items))
    log.info('Groupme received the following args: {}'.format(request.args.items))
    name = request.args['name'].lower()
    test = request.args['text']
    possibilities = [
        'shut the fuck up Ishan',
        'sHuT ThE fUCk uP iSHaN',
        'Shut the FUCK up Ishan'
    ]
    selection = random.randint(0,2)
    if name == 'max amsterdam':
        r = requests.post('https://api.groupme.com/v3/bots/post', params={"text" : possibilities[selection], "bot_id" : "366a7bac14fc9609ff18849b6b"})
    return Response('Received and sent a message!')
    
@groupme.route("/groupme/ishanbot", methods=['POST'])
def ishanbot():
    log.info('Groupme received the following args: {}'.format(request.args.items))
    name = request.args['name'].lower()
    test = request.args['text']
    possibilities = [
        'shut the fuck up Ishan',
        'sHuT ThE fUCk uP iSHaN',
        'Shut the FUCK up Ishan'
    ]
    selection = random.randint(0,2)
    if name == 'ishan django':
        r = requests.post('https://api.groupme.com/v3/bots/post', params={"text" : possibilities[selection], "bot_id" : "8ac02d8d84c2cae7301c0f5a5d"})
    return Response('Received and sent a message!')