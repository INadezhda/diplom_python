import time
from pprint import pprint
import vk_api
from datetime import datetime
from vk_api import VkUpload
from random import randrange
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.upload import VkUpload
from chatbot_bd import Create_tables, find_user_vk, add_user_vk, count_offset
from chat_bot import acquaintance_me, acquaintance_you, get_photos, get_user_city
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

with open('config.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    token = lines[1]
    vk_token = lines[3]

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)
upload = VkUpload(vk)


def write_msg(user_id, message, attachment=None):
    vk.method('messages.send',
              {'user_id': user_id,
               'message': message,
               'attachment': attachment,
               'random_id': randrange(10 ** 7),
               })


def see_photos(user_search_id):
    # photo_list = get_photos(user_search_id=user['id'], vk_token=vk_token)
    photo_list = get_photos(user_search_id, vk_token=vk_token)
    attachment = ' '
    for photo in photo_list:
        attachment += f'photo{photo["owner_id"]}_{photo["id_photo"]},'
    return attachment

def find_user(user_spr, user_msg):
    spr = []
    for i in user_spr:
        find = find_user_vk(user_id=i['id'])
        if find is None:
            spr.append(i)
    if spr != []:
        user = spr.pop()
        attachment = see_photos(user_search_id=user['id'])
        write_msg(
            user_msg,
            f'{user["name"]}  vk.com/{user["id"]}',
            attachment=attachment)
        add_user_vk(user_id=user['id'])
        write_msg(user_msg, f'продолжим поиск?(да/нет)')
    else:
        return 0


def check_user_info(res, user_id):
    if res['bdate'] is None:
        write_msg(user_id, f'Введите дату рождения дд.мм.гггг:')
        # bdate = lambda d: datetime.strptime(d, '%d.%m.%Y').date() <= datetime.today().date()
        text = input_user_bdate(longpoll=longpoll)
        bdate = {'bdate': text}
        res.update(bdate)
    if res['sex'] is None:
        write_msg(user_id, f'Введите пол м/ж:')
        text = input_user_sex(longpoll)
        sex = {'sex': 1} if text == 'ж' else {'sex': 2}
        res.update(sex)
    if res['home_town'] is None:
        write_msg(user_id, f'Введите название своего родного города:')
        title = input_user_town(longpoll)
        text = {'home_town': title}
        res.update(text)
    if res['relation'] is None:
        if res['sex'] == 2:
            write_msg(user_id, f'Введите семейное положение:'
                      f'  1: не женат,'
                      f'  2: есть друг,'
                      f'  3: помолвлен,'
                      f'  4: женат,'
                      f'  5: все сложно,'
                      f'  6: в активном поиске,'
                      f'  7: влюблен,'
                      f'  8: в гражданском браке,'
                      f'  9: не указано')
        else:
            write_msg(user_id, f'Введите семейное положение:'
                      f'  1: не замужем,'
                      f'  2: есть подруга,'
                      f'  3: помолвлена,'
                      f'  4: замужем,'
                      f'  5: все сложно,'
                      f'  6: в активном поиске,'
                      f'  7: влюблена,'
                      f'  8: в гражданском браке,'
                      f'  9: не указано')
        family_position = input_family_position(longpoll)
        text = {'relation': int(family_position)}
        res.update(text)
    # pprint(res)
    return res


def input_user_bdate(longpoll):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                while True:
                    try:
                        datetime.strptime(request, '%d.%m.%Y')
                        # bdate = lambda d: datetime.strptime(d, '%d.%m.%Y').date() <= datetime.today().date()
                        write_msg(event.user_id, f'принято')
                        return request
                    except ValueError as e:
                        write_msg(event.user_id,
                                  f'{e} введите корректную дату рождения')
                        break


def input_user_sex(longpoll):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                sex = {'ж': 1, 'м': 2}
                while True:
                    if request in sex.keys():
                        write_msg(event.user_id, f'принято')
                        return request
                    else:
                        write_msg(event.user_id, f'введите корректный пол')
                        break


def input_user_town(longpoll):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                while True:
                    spr_town = get_user_city(town=request, vk_token=vk_token)
                    if spr_town == 1:
                        title = request
                        write_msg(event.user_id, f'принято')
                        return title
                    else:
                        write_msg(
                            event.user_id,
                            f'введите корректное название населенного пункта')
                        break


def input_family_position(longpoll):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                while True:
                    family_position = request
                    if family_position.isdigit() == True:
                        write_msg(event.user_id, f'принято')
                        return family_position
                    else:
                        write_msg(event.user_id,
                                  f'введите семейное положение корректно:')
                        break


def filter_user_spr(user_spr):
    filter_spr = []
    filter_no_spr = []
    for i in user_spr:
        find = find_user_vk(user_id=i['id'])
        if find is None:
            filter_spr.append(i)
        else:
            filter_no_spr.append(i)
        if len(filter_no_spr) == len(user_spr):
            return 0
        elif len(filter_spr) > 0:
            return user_spr


def bot_communication(longpoll):

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                # res = acquaintance_me(user_id=event.user_id, token=token)
                if request == 'привет':
                    res = acquaintance_me(user_id=event.user_id, token=token)
                    write_msg(event.user_id, f'привет, {res["name"]}')
                elif request == 'пока':
                    write_msg(event.user_id, f'пока')
                elif request == 'давай познакомимся':
                    res = acquaintance_me(user_id=event.user_id, token=token)
                    write_msg(event.user_id, f'можно попробовать')
                    res = check_user_info(res=res, user_id=event.user_id)
                    offset = count_offset()
                    user_spr = acquaintance_you(
                        res, offset=offset, vk_token=vk_token)
                    while True:
                        condition = filter_user_spr(user_spr)
                        if condition == 0:
                            print(f'снова пустой поиск')
                            offset = offset + 30
                            user_spr = acquaintance_you(res, offset, vk_token)
                        else:
                            break
                    find_user(user_spr, user_msg=event.user_id)
                elif request == 'нет':
                    write_msg(event.user_id, f'жаль')
                elif request == 'да':
                    x = find_user(user_spr, user_msg=event.user_id)
                    if x == 0:
                        offset = offset + 30
                        user_spr = acquaintance_you(
                            res, offset=offset, vk_token=vk_token)
                        while True:
                            condition = filter_user_spr(user_spr)
                            if condition == 0:
                                print(f'снова пустой поиск')
                                offset = offset + 30
                                user_spr = acquaintance_you(
                                    res, offset, vk_token)
                            else:
                                find_user(user_spr, user_msg=event.user_id)
                                break
                else:
                    write_msg(event.user_id, f'не понимаю о чем вы ')


Create_tables()
bot_communication(longpoll=longpoll)
