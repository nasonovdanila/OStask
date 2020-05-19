import vk_api
from time import sleep
import json
from multiprocessing import Process, Pipe, current_process
from threading import Thread
import os.path
import psutil
import timeit

def listener(type, ppid,chld_pipe,isTest):
    if psutil.pid_exists(ppid) and not isTest:
        print(f"Listening of type {type}")
        sleep(wait_time)
        if chld_pipe.recv() == 'ping':
            psutil.Process(pid=ppid).terminate()
            print(f'Type {type} terminated by listener')
            chld_pipe.close()

def parse_news(new: dict, type: int, chld_pipe, isTest):
    listen = Process(target=listener, args=(type,current_process().pid,chld_pipe,isTest))
    listen.start()

    if type != 3:
        if type == 0:
            parsed_new = {'id' : new['id'], 'text' : new['text']}
            current_process().name = 'Type 0'
        elif  type == 1:
            parsed_new = {'id' : new['id'], 'pics' : new['pics'], 'url' : new['url']}
            current_process().name = 'Type 1'
        else:
            parsed_new = {'id' : new['id'], 'url' : new['url']}
            current_process().name = 'Type 2'
        
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
        
        if isTest:
            os.remove(f'./news_type{type}.json')
    else:
        sleep(300)
        current_process().name = 'Type 3'
    
    listen.terminate()
    if not isTest: print(f"pr end {current_process().name}")
    
    
    
if __name__ == "__main__":

    main_pid = os.getpid()
    news_parsed = []
    news = None
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
    pipes = []

    wait_time = 0.0
    for num in range(3):
        st = timeit.default_timer()
        parse_news(news_parsed[0],num,True,True)
        new_time = timeit.default_timer() - st
        if wait_time == None:
            wait_time = new_time
        else:
            if new_time > wait_time: wait_time = new_time


    for new in news_parsed:
        print(f"News num {new['id']}")
        for num in range(4):
            pipes.append(Pipe())
            processes.append(Process(target=parse_news, args=(new, num, pipes[num][0], False)))

        for num in range(4):
            processes[num].start()
        
        sleep(wait_time)
        
        stucked_proc = [processes.index(proc) for proc in processes if proc.is_alive()]
        
        if len(stucked_proc) != 0: 
            sleep(2.0)

            for num in stucked_proc:
                if processes[num].is_alive():
                    pipes[num][1].send("ping")
        
            sleep(4.0)

            for num in stucked_proc:
                if processes[num].is_alive():
                    processes[num].terminate()
                    print(f"Killed from main type {num}")
                    
        
        for num in range(4):
            processes[num].join()
        processes = []
        pipes = []


"""
TODO
for new in news:
    читаю аутпут после какого-то времени
    если умерли, то перезапустить
    читаю время и суммирую в 3 переменные 
    каждый 5тый прогон менять их порядок в зависимости от времени отклика

"""