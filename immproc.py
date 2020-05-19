import vk_api
from time import sleep
import json
from multiprocessing import Process, Queue, current_process
from threading import Thread
import os.path
from psutil import pid_exists

def listener(type, qu, ppid):
    if pid_exists(ppid):
        print(f"Listening of type {type+1}")
        sleep(5)
        print(f"Too long processing of type {type+1}")


    pass

def parse_news(news: list, type: int, qu_type: Queue, qu_ping: Queue):
    listen = Process(target=listener, args=(type,qu_ping,current_process().pid,))
    listen.start()

    if type != 3:
        processed_news = []
        for new in news:
            if type == 0:
                current_process().name = 'Type 1'
                processed_news.append({'id' : new['id'], 'text' : new['text']})
            elif  type == 1:
                current_process().name = 'Type 2'
                processed_news.append({'id' : new['id'], 'pics' : new['pics'], 'url' : new['url']})
            else:
                current_process().name = 'Type 3'
                processed_news.append({'id' : new['id'], 'url' : new['url']})
            
            if not os.path.exists(f'./news_type{type+1}.json'):
                with open(f'./news_type{type+1}.json','w+') as a: pass

        with open(f'./news_type{type+1}.json','w+') as news_json:
            news_json.write(json.dumps(processed_news, indent=1))
    else:
        sleep(3)
        current_process().name = 'Type BAD'
    
    listen.terminate()
    print(f"pr end {current_process().name}")
    
    
    
if __name__ == "__main__":

    main_pid = os.getpid()
    news_parsed = []
    download = input('Скачать новости ? (Y/n): ')
    
    if download == 'Y' or download == '':
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
    else:
        with open('./news_parsed.json','r') as news_json:
            news_parsed = json.loads(news_json.read())

    processes = []
    pids = []
    queues = []

    for num in range(4):
        queues.append(Queue())
        processes.append(Process(target=parse_news, args=(news_parsed,num,queues[num],)))

    for num in range(4):
        processes[num].start()





    for num in range(4):
        processes[num].join()
    processes = []
    queues = []


"""
TODO
for new in news:
    читаю аутпут после какого-то времени
    если умерли, то перезапустить
    читаю время и суммирую в 3 переменные 
    каждый 5тый прогон менять их порядок в зависимости от времени отклика

"""