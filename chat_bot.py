import json
import sqlalchemy as sq
import psycopg2
from datetime import datetime
from pprint import pprint
import requests


def acquaintance_me(user_id, token):
    url_user = 'https://api.vk.com/method/users.get'
    params = {
        'user_ids': user_id,
        'access_token': token,
        'v': '5.131',
        'fields': 'sex,relation,city,bdate,home_town,relation'
    }
    try:
        res = requests.get(url_user, params=params).json()['response'][0]

    except ApiError as e:
        res = {}
        print(f'error={e}')

    result = {
        'name': res['first_name'] + ' ' + ' ' + res['last_name'],
        'sex': res.get('sex'),
        'city': res.get('city')['id'],
        'bdate': res.get('bdate'if 'bdate' in res else None),
        'home_town': res.get('home_town') if 'home_town' in res else None,
        'relation': res.get('relation') if 'relation' in res else None}

    return result


def acquaintance_you(res, offset, vk_token):
    sex = 2 if res['sex'] == 1 else 1
    city = res['city']
    curent_year = datetime.now().year
    user_year = int(res['bdate'].split('.')[2])
    age = curent_year - user_year
    age_from = age - 5
    age_to = age + 5
    relation = res['relation']
    url_user = 'https://api.vk.com/method/users.search'
    params = {
        'access_token': vk_token,
        'v': '5.131',
        'count': 30,
        'offset': offset,
        'age_from': age_from,
        'age_to': age_to,
        'sex': sex,
        'city': city,
        'status': 6,
        'is_closed': False,
        'has_photo': True
    }
    try:
        result = requests.get(url_user, params=params).json()['response']['items']
    except ValueError as e:
        result = {}
        print(f'error{e}')

    user_spr = []
    for user in result:
        if not user['is_closed']:
            user_spr.append(
                {'id': user['id'], 'name': user['first_name'] + ' ' + user['last_name']})
    return user_spr


def get_photos(user_search_id, vk_token):
    url_user = 'https://api.vk.com/method/photos.get'
    params = {
        'v': '5.131',
        'access_token': vk_token,
        'owner_id': user_search_id,
        'album_id': 'profile',
        'extended': 1
    }
    try:
        result = requests.get(url_user, params=params).json()
    except KeyError:
        return []

    photo_list = []
    result = result['response']['items']
    for photo in result:
        photo_list.append({'owner_id': photo['owner_id'],
                          'id_photo': photo['id'],
                           'likes': photo['likes']['count'],
                           'comment': photo['comments']['count']})

    photo_list = sorted(photo_list, key=lambda x: x['likes'] * 10 + x['comment'], reverse=True)[:3]
    return photo_list


def get_user_city(town, vk_token):
    url_user = 'https://api.vk.com/method/database.getCities'
    params = {
        'access_token': vk_token,
        'v': '5.131',
        'country_id': 1,
        'q': town,
        'offset': 0,
        'count': 10
    }
    headers = {'Content-type': 'application/json',
               'Content-Encoding': 'utf-8'}
    response = requests.get(url_user, headers=headers, params=params).json()
    result = response['response']['items']
    if result:
        return 1
    else:
        return 0
