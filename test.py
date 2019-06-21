import os
import re
from nltk.tokenize import sent_tokenize


def clean_content(content):
    noise_words = re.findall(r"<[^/][^>]+?>(.+?)</.+?>",content)
    # print (noise_words)
    for word in noise_words:
        s = ''
        for _ in range(len(word)): # 把同一行标签内的文字替换成空格
            s = s + " "
        pad_word = '>' + s + '<'
        content = content.replace('>'+word+'<',pad_word)
    content = re.sub("<.+?>|<\/.+?>", "", content) # 去除剩下的标签
    return content

# with open("D:/ACE/LDC2006T06/data/English/bc/timex2norm/CNN_CF_20030303.1900.00.sgm", "r", encoding='utf-8') as f:
#     content = f.read()
# content = clean_content(content)
# content = content.replace("\n"," ")
# sentence_str = sent_tokenize(content)
# for i,sent in enumerate(sentence_str):
#     print (i, sent)

# total = 0
# count = 0
# for path in ['D:/ACE/LDC2006T06/data/English/bc/timex2norm/','D:/ACE/LDC2006T06/data/English/bn/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/cts/timex2norm/','D:/ACE/LDC2006T06/data/English/nw/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/un/timex2norm/','D:/ACE/LDC2006T06/data/English/wl/timex2norm/']:

#     filelist = os.listdir(path)
#     for i,filename in enumerate(filelist):
        
#         if filename.endswith(".sgm"):
#             count += 1
#             # print ("{i} / {total} {filename}  running ...".format(i=(i+1)//4+1, total=total//4,filename=filename))    
#             apf_filename = path + filename

#             with open(apf_filename, "r", encoding='utf-8') as f:
#                content = f.read()

#             content = clean_content(content)
#             content = content.replace("\n"," ")
#             sentence_str = sent_tokenize(content)
#             total += len(sentence_str)
#             print (filename, len(sentence_str), total)
# print ("total sents: ", total)
# print ("count: ", count)

import json
with open("D:/ACE/anno_event_json2/MARKBACKER_20041117.1107.json",'r') as load_f:
    event_list = json.load(load_f)
    # print (event_list)

for event in event_list:
    print (event)
    for kkey in event:
        print (event[kkey])