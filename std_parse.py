# 用standfordCoreNLP把sgm解析成句子

# 先全部标完，再检查readme中的特殊情况(event extent中多个事件之类...)

"""
    从./event_json/XXX.json读出事件要素信息，在原文中查找对应的句子，
    标注句中每个token相对全文的offset,并用stnadfordNLP对句子进行标注,
    结果写入./event_anno_json/XXX.json
"""

from stanfordcorenlp import StanfordCoreNLP
from nltk.tokenize import sent_tokenize
import re
import os
import json

nlp = StanfordCoreNLP(r'E:/Standford NLP/stanford-corenlp-full-2018-10-05/', lang='en')
anno_event_path = "D:/ACE/anno_event_json/"

def find_offset(sentence_start, sentence, tokens):
    
    padding = "".join(["*" for _ in range(len(sentence))])
    token_seq = []
    for token in tokens:
        start = sentence.find(token)
        end = start + len(token)
        sentence = padding[:end] + sentence[end:]
        global_start, global_end = start+sentence_start, end+sentence_start-1 # 由于ACE对end的标注小1，所以比对时注意这里减1
        token_seq.append((global_start,global_end))
        # print (token, global_start, global_end)
        # print (sentence)
        # print ("\n")
    return token_seq


def clean_content(content):
    noise_words = re.findall(r"<[^/][^>]+?>(.+?)</.+?>",content)
    # print (noise_words)
    for word in noise_words:
        s = ''
        for _ in range(len(word)): # 把同一行标签内的文字替换成空格
            s = s + " "
        pad_word = '>' + s + '<'
        content = content.replace('>'+word+'<',pad_word)
    content = re.sub("<.+?>|<\/.+?>|<QUOTE[\s\S][^>]+?>", "", content) # 去除剩下的标签
    return content


def parse_event(filename, sgm_filename, json_filename):
    """ 
        filename: AFP_ENG_20030401.0476 原始article_id
        sgm_filename: 原始的sgm文件
        json_filename: 抽取sgm文件中事件得到的json文件
    """

    with open(sgm_filename, "r", encoding='utf-8') as f:
       content = f.read()

    with open(json_filename,'r') as load_f:
        event_list = json.load(load_f)

    content = clean_content(content)
    content = content.replace("\n"," ")
    sentence_str = sent_tokenize(content) # 将content划分句子后的结果
    sentence_num = len(sentence_str)


    for index,event_mention in enumerate(event_list):            
        event = {}
        event["article_id"],event["event_id"] = filename, event_mention["event_id"]
        event["event_type"], event["event_subtype"] = event_mention["event_type"], event_mention["event_subtype"]
        event_start, event_end = int(event_mention["start"]), int(event_mention["end"])

        i = 0
        while i < len(sentence_str):

            sentence = sentence_str[i].strip()
            sentence_start = content.find(sentence)
            sentence_end = sentence_start + len(sentence)

            # print ("event_start: ", event_start, "event_end: ",event_end, "sentence_start: ", sentence_start, "sentence_end: ",sentence_end)
            if sentence_start <= event_start and sentence_end >= event_end + 1: # 注意这个+1, .apf.xml中的end需要再+1才是index
                # print ("sentence: ", sentence)
                sentence_id = hash(filename+sentence)   
                event["sentence_id"], event["sentence"], event["sentence_start"], event["sentence_end"] = sentence_id, sentence, sentence_start, sentence_end
                tokens = nlp.word_tokenize(sentence)
                event["tokens"], event["pos"], event["ner"], event["dependency"] = tokens, nlp.pos_tag(sentence), nlp.ner(sentence), nlp.dependency_parse(sentence)
                event["trigger"], event["trigger_start"], event["trigger_end"] = event_mention["trigger"], event_mention["trigger_start"], event_mention["trigger_end"]
                event["arguments"] = event_mention["arguments"]
                tokens_offset = find_offset(sentence_start, sentence, tokens)
                event["tokens_offset"] = tokens_offset
                # print ("event: ", event, "\n")

                if index != len(event_list)-1:
                    f.write(json.dumps(event)+",\n")
                else:
                    f.write(json.dumps(event))
                # print (event)
                break # 说明找到了句子
            else:
                i = i + 1



parse_event("CNN_ENG_20030626_193133.8","D:/ACE/LDC2006T06/data/English/bn/timex2norm/CNN_ENG_20030626_193133.8.sgm","D:/ACE/event_json/CNN_ENG_20030626_193133.8.json" )

# json_path = "D:/ACE/event_json/"
# for path in ['D:/ACE/LDC2006T06/data/English/bc/timex2norm/','D:/ACE/LDC2006T06/data/English/bn/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/cts/timex2norm/','D:/ACE/LDC2006T06/data/English/nw/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/un/timex2norm/','D:/ACE/LDC2006T06/data/English/wl/timex2norm/']:
#     filelist = os.listdir(path)
#     total = len(filelist)
#     for i,filename in enumerate(filelist):
#         if filename.endswith(".sgm"):
#             print ("{i} / {total} {filename}  running ...".format(i=(i+1)//4+1, total=total//4,filename=filename))    
#             sgm_filename = path + filename
#             json_filename = json_path + filename.replace(".sgm", ".json")
#             filename = filename[:filename.find(".sgm")]
#             try:
#                 parse_event(filename, sgm_filename, json_filename)
#             except:
#                 print ("==================================")
#                 print (filename)
#                 print ("==================================")
#             # break
nlp.close()