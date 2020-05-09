import vk_api
import time
import json

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
