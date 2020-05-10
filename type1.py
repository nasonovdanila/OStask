import json

with open('./news_parsed.json','r') as news_parsed:
    news_unprocc = json.loads(news_parsed.read())

news_procc = []

for new in news_unprocc:
    news_procc.append({'id' : new['id'], 'text' : new['text']})
    with open('./news_type1.json','w+') as news_json:
        news_json.write(json.dumps(news_procc, indent=1))
