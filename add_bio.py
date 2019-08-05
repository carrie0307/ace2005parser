import json
import os
import xml.etree.cElementTree as ET

"""
    对Standford标注好的数据(./event_anno_json/XXX.json)加上根据.apf.xml中标注的entity、value和Time进行BIO标注

    存在的一个bug:对于一些entity/time/value都不包含的句子，将会出现没有bio的情况(例如:un/rec.arts.mystery_20050219.1126)。这里代码不改了，进行train/dev/test划分时进行修改
"""

ini_anno_path = "D:/ACE/anno_event_json/"
new_anno_path = "D:/ACE/anno_event_json2/"



def add_bio2anno(filename, apf_filename, anno_filename):
    """
        filename = "MARKBACKER_20041117.1107"
        apf_filename = "D:/ACE/LDC2006T06/data/English/wl/timex2norm/MARKBACKER_20041117.1107.apf.xml"
        anno_filename = "D:/ACE/anno_event_json/MARKBACKER_20041117.1107.json"
    """
    # with open("D:/ACE/anno_event_json/MARKBACKER_20041117.1107.json",'r') as load_f:
    with open(anno_filename,'r') as load_f:
        event_list = json.load(load_f)

    # tree = ET.ElementTree(file="D:/ACE/LDC2006T06/data/English/wl/timex2norm/MARKBACKER_20041117.1107.apf.xml")
    tree = ET.ElementTree(file=apf_filename)
    for element in tree.iter():
        
        if element.tag == 'entity':
            entity = element
            # 构建argument词典
            ttype, subtype, cclass = entity.attrib["TYPE"], entity.attrib["SUBTYPE"], entity.attrib["CLASS"]
            for entity_mention in entity.iter(tag="entity_mention"):
                entity_mention_id = entity_mention.attrib["ID"]
                extent_start, extent_end, extent_text = \
                              int(entity_mention[0][0].attrib["START"]), int(entity_mention[0][0].attrib["END"]), entity_mention[0][0].text
                head_start, head_end, head_text = int(entity_mention[1][0].attrib["START"]), int(entity_mention[1][0].attrib["END"]), entity_mention[1][0].text

                for event in event_list:

                    if extent_start >= event["sentence_start"] and extent_end+1 <= event["sentence_end"]:
                        length = len(event["tokens"])
                        if "bio" not in event:
                            event["bio"] = ['O'] * length
                        for i,(start, end) in enumerate(event["tokens_offset"]):
                            if start == extent_start:
                                event["bio"][i] = subtype + '-B'
                            elif extent_start < start and extent_end >= end:
                                event["bio"][i] = subtype + '-I'
                            # 不能break,因为下一个event中可能也有当前entitm mention

        elif element.tag == 'timex2':
            timex2 = element
            # 构建element词典
            for timex2_mention in timex2.iter(tag="timex2_mention"):
                timex2_mention_id = timex2_mention.attrib["ID"]
                extent_start, extent_end = int(timex2_mention[0][0].attrib["START"]), int(timex2_mention[0][0].attrib["END"])

                for event in event_list:
                    if extent_start >= event["sentence_start"] and extent_end+1 <= event["sentence_end"]:
                        length = len(event["tokens"])
                        if "bio" not in event:
                            event["bio"] = ['O'] * length
                        for i,(start, end) in enumerate(event["tokens_offset"]):
                            if start == extent_start:
                                event["bio"][i] = 'Time-B'
                            elif extent_start < start and extent_end >= end:
                                event["bio"][i] = 'Time-I'            

        elif element.tag == 'value':
            value = element
            # 构建argument词典
            if "SUBTYPE" in value.attrib.keys():
                ttype, subtype = value.attrib["TYPE"], value.attrib["SUBTYPE"]
            else:
                ttype, subtype = value.attrib["TYPE"], ""

            for value_mention in value.iter(tag="value_mention"):
                
                extent_start, extent_end = int(value_mention[0][0].attrib["START"]), int(value_mention[0][0].attrib["END"])
                for event in event_list:
                    if extent_start >= event["sentence_start"] and extent_end+1 <= event["sentence_end"]:
                        length = len(event["tokens"])
                        if "bio" not in event:
                            event["bio"] = ['O'] * length
                        for i,(start, end) in enumerate(event["tokens_offset"]):
                            if start == extent_start:
                                event["bio"][i] = subtype + '-B' if subtype else ttype + '-B'
                            elif extent_start < start and extent_end >= end:
                                event["bio"][i] = subtype + '-I' if subtype else ttype + '-I'
                    # print (event["tokens"])
                    # print (event["bio"])
                    # print ("\n")

    # for event in event_list:
    #     if "bio" not in event:
    #         print (event)

    with open(new_anno_path + filename + ".json", "a", encoding='utf-8') as writer:
        print (new_anno_path+filename)
        writer.write("[")
        for i,event in enumerate(event_list):
            writer.write("{") # 一个事件开始
            for j,kkey in enumerate(event):

                if j != len(event)-1:
                    writer.write("\"" + kkey + "\":"+json.dumps(event[kkey])+",\n")
                else:
                    writer.write("\"" + kkey + "\":"+json.dumps(event[kkey]))
            if i != len(event_list)-1:
                writer.write("},\n") # 一个事件结束
            else:
                writer.write("}")
        writer.write("]")

add_bio2anno("rec.arts.mystery_20050219.1126", "D:/ACE/LDC2006T06/data/English/un/timex2norm/rec.arts.mystery_20050219.1126.apf.xml", "D:/ACE/anno_event_json/rec.arts.mystery_20050219.1126.json")
# CNN_ENG_20030617_193116.10.json

# for path in ['D:/ACE/LDC2006T06/data/English/bc/timex2norm/','D:/ACE/LDC2006T06/data/English/bn/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/cts/timex2norm/','D:/ACE/LDC2006T06/data/English/nw/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/un/timex2norm/','D:/ACE/LDC2006T06/data/English/wl/timex2norm/']:
#     filelist = os.listdir(path)
#     total = len(filelist)
#     for i,filename in enumerate(filelist):
#         if filename.endswith(".apf.xml"):
#             apf_filename = path + filename
#             anno_filename = ini_anno_path + filename.replace(".apf.xml", ".json")
#             filename = filename[:filename.find(".apf.xml")]
#             print ("{i} / {total} {filename}  running ...".format(i=(i+1)//4+1, total=total//4,filename=filename))
#             try:
#                 add_bio2anno(filename, apf_filename, anno_filename)
#             except:
#                 print ("==============")
#                 print (filename)
#                 print ("==============")

