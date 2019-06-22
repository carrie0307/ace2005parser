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
anno_event_path = "D:/ACE/anno_event_json3/"

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


"""
注意，为了正文中SPEAK等标签中的word不对分句产生影响，clean_content()函数中通过noise_words进行了过滤。
然而un目录下的部分documnt存在标签内容包含事件的情况，因此注释掉noise_word部分代码，单独对这部分articles进行了处理
alt.obituaries_20041121.1339
alt.religion.mormon_20050103.0854
alt.sys.pc-clone.dell_20050226.2350
misc.legal.moderated_20041202.1648
misc.taxes_20050218.1250
rec.boats_20050130.1006
rec.music.makers.guitar.acoustic_20041228.1628
rec.music.phish_20050217.1804
rec.travel.cruises_20050216.1636
rec.travel.usa-canada_20050128.0121
soc.culture.china_20050203.0639
soc.culture.indian_20041104.2348
soc.culture.iraq_20050211.0445
soc.culture.jewish_20050130.2105
soc.history.war.world-war-ii_20050127.2403
soc.history.what-if_20050129.1404
soc.org.nonprofit_20050218.1902
"""

def clean_content(content):
    # noise_words = re.findall(r"<[^/][^>]+?>(.+?)</.+?>",content)
    # # print (noise_words)
    # for word in noise_words: # 主要针对SPEAK等,但要注意
    #     s = ''
    #     for _ in range(len(word)): # 把同一行标签内的文字替换成空格
    #         s = s + " "
    #     pad_word = '>' + s + '<'
    #     content = content.replace('>'+word+'<',pad_word)
    content = re.sub("<.+?>|<\/.+?>|<QUOTE[\s\S][^>]+?>", "", content) # 去除剩下的标签
    # content = re.sub("<.+?>|<\/.+?>", "", content) # 去除剩下的标签
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

    with open(anno_event_path + filename + ".json", "a", encoding='utf-8') as writer:
        writer.write("[")
        for index,event_mention in enumerate(event_list):    
         
            event = {}
            event["article_id"],event["event_id"] = filename, event_mention["event_id"]
            event["event_type"], event["event_subtype"] = event_mention["event_type"], event_mention["event_subtype"]
            event_start, event_end = int(event_mention["start"]), int(event_mention["end"])
            trigger_start, trigger_end = int(event_mention["trigger_start"]), int(event_mention["trigger_end"])

            i = 0
            sentence_start, sentence_end = 0, 0
            while i < len(sentence_str):
      
                sentence = sentence_str[i].strip()
                sentence_start = content[sentence_end:].find(sentence) + sentence_end
                sentence_end = sentence_start + len(sentence)
               
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
                        writer.write(json.dumps(event)+",\n")
                    else:
                        writer.write(json.dumps(event))
                    break # 说明找到了句子
                elif sentence_start <= trigger_start and sentence_end >= trigger_end + 1:
                    # 部分evetn_extent无法完全匹配上sentence,因此再用trigger过滤一遍(在实验中发现，只有52个event_Extent有这种情况)
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
                        writer.write(json.dumps(event)+",\n")
                    else:
                        writer.write(json.dumps(event))
                    break # 说明找到了句子
                else:
                    i = i + 1
        writer.write("]")


# with open("D:/ACE/LDC2006T06/data/English/un/timex2norm/alt.obituaries_20041121.1339.sgm", "r", encoding='utf-8') as f:
#        content = f.read()
# content = clean_content(content)
# content = content.replace("\n"," ")
# print (content)
# print (content[143:164])
# sentence_str = sent_tokenize(content)
# for i,sent in enumerate(sentence_str):
#     sent = sent.strip()
#     print (sent, content.find(sent), content.find(sent)+len(sent))

with open("temp", "r", encoding='utf-8') as f:
    filenames = f.readlines()

for filename in filenames:
    filename = filename.split(" ")[0]
# filename = "BACONSREBELLION_20050127.1017"
    parse_event(filename,"D:/ACE/LDC2006T06/data/English/nw/timex2norm/"+filename+".sgm","D:/ACE/event_json/"+filename+".json" )

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