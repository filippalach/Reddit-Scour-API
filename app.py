#!/usr/bin/env python3.7

import re
import time
import json
import datetime

import connexion
from connexion import NoContent
import six
from werkzeug.exceptions import Unauthorized
from jose import JWTError, jwt
import praw
from prawcore.exceptions import Redirect, NotFound

import orm

# jwt
PATH_TO_CLIENT_ID = '/home/ubuntu/.secrets/jwt_hs'

with open(PATH_TO_CLIENT_ID) as jwt_secret:
    JWT_SECRET = jwt_secret.read().replace('\n', '')

JWT_ISSUER = 'some-kind-of-issuer'
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'

# praw
PATH_TO_CLIENT_ID = '/home/ubuntu/.secrets/client_id'
PATH_TO_CLIENT_SECRET = '/home/ubuntu/.secrets/client_secret'
PATH_TO_USER_AGENT = '/home/ubuntu/.secrets/user_agent'

with open(PATH_TO_CLIENT_ID) as client_id:
    CLIENT_ID = client_id.read().replace('\n', '')
with open(PATH_TO_CLIENT_SECRET) as client_secret:
    CLIENT_SECRET = client_secret.read().replace('\n', '')
with open(PATH_TO_USER_AGENT) as user_agent:
    USER_AGENT = user_agent.read().replace('\n', '')

db_session = orm.init_db('sqlite:///:memory:')
app = connexion.FlaskApp(__name__)
app.add_api('openapi.yaml')

application = app.app

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

def retrieve_posts(subreddit, number):
    subreddit = reddit.subreddit(subreddit)

    posts = {}

    try:
        for x, post in enumerate(subreddit.hot(limit=number)):
            posts[x] = post.title
    except Redirect:
        return {'error': f'Subreddit {subreddit} not found' }, 404

    return posts, 200
   
def find_phrase_post(subreddit, phrase):
    subreddit = reddit.subreddit(subreddit)

    try:
        for post in subreddit.hot(limit=30):
            if phrase in post.title:
                payload = {
                    'id': post.id,
                    'title': post.title,
                    'url': post.permalink
                }
                return payload, 200
    except Redirect:
        return {'error': f'Subreddit {subreddit} not found' }, 404

    return { 'error': f'Not found {phrase} in latest posts on {subreddit} subreddit.' }, 404

def count_phrase_comments(post_id, phrase):
    try:
        comments = ''

        submission = reddit.submission(id=post_id)

        submission.comments.replace_more(limit=None)
    except NotFound:
        return {'error': f'Post {post_id} not found' }, 404
    for top_level_comment in submission.comments.list():
        comments += top_level_comment.body

    comments.split()

    return comments.count(phrase), 200

def picture_post(post_id):
    try:
        submission = reddit.submission(id=post_id)

        return_data = {
            'url': submission.url
        }
    except NotFound:
        return {'error': f'Post {post_id} not found' }, 404

    return return_data, 200

def subscribers_subreddit(subreddit):
    subreddit = reddit.subreddit(subreddit)

    try:
        return_data = {
            'subscribers': subreddit.subscribers
        }
    except Redirect:
        return {'error': f'Subreddit {subreddit} not found' }, 404

    return return_data, 200

def get_drivers():
    subreddit = reddit.subreddit('formula1')

    post_ids = []
    comments = ''
    
    for post in subreddit.hot(limit=20):
        post_ids.append(post.id)

    for post_id in post_ids:
        submission = reddit.submission(id=post_id)
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments.list():
            comments += top_level_comment.body

    return _drivers(comments), 200

def put_drivers(driver_id):
    subreddit = reddit.subreddit('formula1')

    post_ids = []
    comments = ''
    
    for post in subreddit.hot(limit=20):
        post_ids.append(post.id)

    for post_id in post_ids:
        submission = reddit.submission(id=post_id)
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments.list():
            comments += top_level_comment.body

    driver = {}

    p = db_session.query(orm.Driver).filter(orm.Driver.id == driver_id).one_or_none()
    driver['id'] = driver_id
    driver['created'] = datetime.datetime.utcnow()
    driver['data'] = _drivers(comments)
    if p is not None:
        p.update(**driver)
    else:
        print('robe')
        db_session.add(orm.Driver(**driver))
    db_session.commit()
    return NoContent, (200 if p is not None else 201)

def get_drivers_id(driver_id):
    driver = db_session.query(orm.Driver).filter(orm.Driver.id == driver_id).one_or_none()
    return driver.dump() if driver is not None else ('Not found', 404)

def delete_drivers_id(driver_id):
    driver = db_session.query(orm.Driver).filter(orm.Driver.id == driver_id).one_or_none()
    if driver is not None:
        print('deleting driver')
        db_session.query(orm.Driver).filter(orm.Driver.id == driver_id).delete()
        db_session.commit()
        return NoContent, 204
    else:
        return NoContent, 404

def generate_token(user_id):
    timestamp = _current_timestamp()

    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user_id),
    }

    return {'jwt': '{}'.format(jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM))}

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)

def get_secret(user, token_info) -> str:
    return {
        'user_id': user,
        'token_info': token_info
    }

def _current_timestamp() -> int:
    return int(time.time())

def _drivers(comments):
    HAM_REG = 'ham|hamilton|lewis'
    BOT_REG = 'bot|bottas|valtteri'
    VET_REG = 'vet|vettel|seb|sebastian'
    LEC_REG = 'lec|leclerc|charles'
    VER_REG = 'ver|verstappen|max'
    ALB_REG = 'alb|albon|alex'
    RIC_REG = 'ric|riccardo'
    OCO_REG = 'oco|ocon|esteban'
    NOR_REG = 'nor|norris|lando'
    SAI_REG = 'sai|sainz|carlos'   
    
    drivers = {
        'ham': len(re.findall(HAM_REG, comments, re.IGNORECASE)),
        'bot': len(re.findall(BOT_REG, comments, re.IGNORECASE)),
        'vet': len(re.findall(VET_REG, comments, re.IGNORECASE)),
        'lec': len(re.findall(LEC_REG, comments, re.IGNORECASE)),
        'ver': len(re.findall(VER_REG, comments, re.IGNORECASE)),
        'alb': len(re.findall(ALB_REG, comments, re.IGNORECASE)),
        'ric': len(re.findall(RIC_REG, comments, re.IGNORECASE)),
        'oco': len(re.findall(OCO_REG, comments, re.IGNORECASE)),
        'nor': len(re.findall(NOR_REG, comments, re.IGNORECASE)),
        'sai': len(re.findall(SAI_REG, comments, re.IGNORECASE)),
    }

    return drivers

if __name__ == '__main__':
    app.run(port=1129, use_reloader=False, threaded=False)