import vk_api
import time
import json
from multiprocessing import Process
import os.path


def parse_news(new, type: int):

    if type == 1:
        parsed_new = {'id' : new['id'], 'text' : new['text']}
    elif  type == 2:
        parsed_new = {'id' : new['id'], 'pics' : new['pics'], 'url' : new['url']}
    else:
        parsed_new = {'id' : new['id'], 'url' : new['url']}
    
    if not os.path.exists(f'./news_type{type}.json'):
        with open(f'./news_type{type}.json','w+') as a: pass

    with open(f'./news_type{type}.json','r') as news_raw:
        news_data = news_raw.read()

    if news_data == '':
        temp = [parsed_new]
    else:
        temp = json.loads(news_data)
        temp.append(parsed_new)

    with open(f'./news_type{type}.json','w+') as news_json:
        news_json.write(json.dumps(temp, indent=1))
    

def bad():
    time.sleep(30)

    
if __name__ == "__main__":

    with open('./.creds.txt','r') as cred:
        cred = cred.read().splitlines()
        client = vk_api.VkApi(cred[0], cred[1])
        try:
            client.auth()
        except Exception as e:
            print(e)

    try:
        news = client.method("newsfeed.get", {"count":100,"filters":['post']})
    except Exception as e:
        print(e)

    news_parsed = []

    for new in news['items']:
        new_pics = []
        if 'attachments' in new:
                for attachment in new['attachments']:
                    if attachment['type'] == 'photo':
                        new_pics.append(attachment['photo']['sizes'][0]['url'])
        new_url = f'https://vk.com/feed?w=wall{new["source_id"]}_{new["post_id"]}'
        news_parsed.append({'id': new['post_id'], 'text': new['text'], 'pics' : new_pics, 'url' : new_url})
    
    with open('./news_parsed.json','w+') as news_json:
        news_json.write(json.dumps(news_parsed, indent=1))

    for new in news_parsed:
        proc1 = Process(target=parse_news, args=(new,1,))
        proc2 = Process(target=parse_news, args=(new,2,))
        proc3 = Process(target=parse_news, args=(new,3,))
        proc_bad = Process(target=bad)
        proc1.start()
        proc2.start()
        proc3.start()
        proc_bad.start()
        proc1.join()
        proc2.join()
        proc3.join()
        proc_bad.join()

"""
TODO
for new in news:
    читаю аутпут после какого-то времени
    если умерли, то перезапустить
    читаю время и суммирую в 3 переменные 
    каждый 5тый прогон менять их порядок в зависимости от времени отклика

"""