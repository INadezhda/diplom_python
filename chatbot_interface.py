from pprint import pprint
import vk_api
from vk_api import VkUpload
from random import randrange
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.upload import VkUpload
from  chatbot_bd import Create_tables,find_user_vk,add_user_vk,count_offset
from chat_bot import acquaintance_me,acquaintance_you,get_photos

with open ('config.txt', 'r', encoding='utf-8') as f:
    lines=f.readlines()
    token=lines[1]
    vk_token=lines[3]

vk=vk_api.VkApi(token=token)
session_api=vk.get_api()
longpoll=VkLongPoll(vk)
upload=VkUpload(vk)

def write_msg(user_id,message, attachment=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'attachment':attachment,'random_id': randrange(10 ** 7),})

def see_photos(user_search_id):
    #photo_list = get_photos(user_search_id=user['id'], vk_token=vk_token)
    photo_list = get_photos(user_search_id,vk_token=vk_token)
    attachment = ' '
    for photo in photo_list:
        attachment += f'photo{photo["owner_id"]}_{photo["id_photo"]},'
    return attachment
def find_user(user_spr):
    spisok=[]
    for i in user_spr:
        user = i
        find = find_user_vk(user_id=user['id'])
        if find == None:
            spisok.append(i)
            attachment = see_photos(user_search_id=user['id'])
            write_msg(event.user_id, f'{user["name"]}  vk.com/{user["id"]}', attachment=attachment)
            add_user_vk(user_id=user['id'])
    if len(spisok)==0:
        write_msg(event.user_id,f'попробую поискать еще(( ')
        #return offset+10
    else:
        write_msg(event.user_id, f'продолжим поиск?(да/нет)')
        return offset+5

for event in longpoll.listen():

    if event.type==VkEventType.MESSAGE_NEW:
         if event.to_me:
              request=event.text.lower()
              res = acquaintance_me(user_id=event.user_id, token=token)
              if request=='привет':
                  write_msg(event.user_id,f'привет, {res["name"]}')
              elif request=='пока':
                  write_msg(event.user_id, f'пока')
              elif request=='давай познакомимся' or request==' начинаем поиск':
                  write_msg(event.user_id,f'можно попробовать')
                  Create_tables()
                  offset = 0
                  user_spr=acquaintance_you(res,offset=offset,vk_token=vk_token)
                  offset=find_user(user_spr)
              elif request=='нет':
                  write_msg(event.user_id,f'жаль')
              elif request=='да':
                  user_spr = acquaintance_you(res, offset=offset, vk_token=vk_token)
                  offset=find_user(user_spr)
              else:
                  write_msg(event.user_id, f'не понимаю о чем вы ')
