import json
import os

data = "test"



with open(data+"_list.txt", "r", encoding='utf-8') as f:
    filenames = f.readlines()

all_event_list = []
for i,filename in enumerate(filenames):
    filename = filename.strip()
    filename = filename.split("/")[-1]
    try:
        with open("D:/ACE/anno_event_json2/" + filename + ".json", "r", encoding='utf-8') as load_f:
            event_list = json.load(load_f)
        all_event_list.extend(event_list)
    except:
        print (filename)

print (len(all_event_list))
content = ''

# 根据句子长度排序
all_event_list.sort(key=lambda k: len(k["tokens"]), reverse=True)
with open("./{data}.json".format(data=data), "a", encoding='utf-8') as writer:
    writer.write("[")
    for i,event in enumerate(all_event_list):
        sentence = " ".join(event["tokens"])
        content = content +sentence + "\n"
        if i != len(all_event_list)-1:
            if "bio" not in event:
                event['bio'] = ['O'] * len(event["tokens"])
            writer.write(json.dumps(event) + ",\n")
        else:
            writer.write(json.dumps(event))
    writer.write("]")

with open("./{data}.txt".format(data=data), "w", encoding='utf-8') as f:
    f.write(content)

# maxLen = 0
# with open("./{data}.json".format(data="test"), "r", encoding='utf-8') as load_f:
#     event_list = json.load(load_f)
# for event in event_list:
#     maxLen = len(event["tokens"]) if (len(event["tokens"]) > maxLen) else maxLen
# print (maxLen)


