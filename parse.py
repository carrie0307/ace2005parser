import xml.etree.cElementTree as ET
import os
import json

"""
    从原始sgm文件中抽取出事件相关要素(event_Extent, trigger, argument)，整合为./event_json/XXX.json文件
"""

json_path = "D:/ACE/event_json/"

def parse_file(filename, apf_filename):
    """
    将apf.xml文件中事件相关信息以json格式解析出来
    """
    # filename = "" # CNN_CF_20030303.1900.02.apf.xml
    tree = ET.ElementTree(file=apf_filename)
    argument_dict = {} # entity, timex2, value
    event_list = [] # 记录所有的event_mention
    event_dict = {} # 某一event_mention的记录

    for element in tree.iter():
        
        if element.tag == 'entity':
            entity = element
            # 构建argument词典
            ttype, subtype, cclass = entity.attrib["TYPE"], entity.attrib["SUBTYPE"], entity.attrib["CLASS"]
            for entity_mention in entity.iter(tag="entity_mention"):
                entity_mention_id = entity_mention.attrib["ID"]
                extent_start, extent_end, extent_text = \
                              entity_mention[0][0].attrib["START"], entity_mention[0][0].attrib["END"], entity_mention[0][0].text
                head_start, head_end, head_text = entity_mention[1][0].attrib["START"], entity_mention[1][0].attrib["END"], entity_mention[1][0].text
                argument_dict[entity_mention_id] = {"type":ttype, "subtype":subtype, "class":cclass,
                                                    "extent_start":extent_start, "extent_end":extent_end, 
                                                    "extent_text":extent_text,"head_start": head_start, 
                                                    "head_end":head_end, "head_text":head_text}

        elif element.tag == 'timex2':
            timex2 = element
            # 构建element词典
            anchor_dir, anchor_val, val = "", "", "" # # timex2.attrib["ANCHOR_DIR"], timex2.attrib["ANCHOR_VAL"] 部分timex2没有这两个属性
            if "VAL" in timex2.attrib.keys():
                val = timex2.attrib["VAL"] 
            if "ANCHOR_DIR" in timex2.attrib.keys():
                anchr_dir = timex2.attrib["ANCHOR_DIR"]
            if "ANCHOR_VAL" in timex2.attrib.keys():
                anchor_val = timex2.attrib["ANCHOR_VAL"]

            for timex2_mention in timex2.iter(tag="timex2_mention"):
                timex2_mention_id = timex2_mention.attrib["ID"]
                extent_start, extent_end, extent_text = timex2_mention[0][0].attrib["START"], timex2_mention[0][0].attrib["END"],timex2_mention[0][0].text
                argument_dict[timex2_mention_id] = {"val":val, "anchor_dir":anchor_dir, "anchor_val":anchor_val, 
                                                    "extent_start":extent_start, "extent_end":extent_end, "extent_text":extent_text}

        elif element.tag == 'value':
            value = element
            # 构建argument词典
            if "SUBTYPE" in value.attrib.keys():
                ttype, subtype = value.attrib["TYPE"], value.attrib["SUBTYPE"]
            else:
                ttype, subtype = value.attrib["TYPE"], ""

            for value_mention in value.iter(tag="value_mention"):
                value_mention_id = value_mention.attrib["ID"]
                extent_start, extent_end, extent_text = value_mention[0][0].attrib["START"], value_mention[0][0].attrib["END"], value_mention[0][0].text
                argument_dict[value_mention_id] = {"type":ttype, "subtype":subtype, "extent_start":extent_start,
                                                   "extent_end": extent_end, "extent_text":extent_text}
            
        elif element.tag == 'event':
            event = element
            event_type, event_subtype = event.attrib["TYPE"], event.attrib["SUBTYPE"]
            # 构建事件相关信息
            for event_mention in event.iter(tag='event_mention'):
                
                # 每遇到一个event_mention,则将上一个event_mention加入列表
                if event_dict:
                    event_list.append(event_dict)
                    event_dict = {}
                for elem in event_mention:
                    if elem.tag == 'extent':
                        start, end, text = elem[0].attrib["START"], elem[0].attrib["END"], elem[0].text # event_mention_extent的内容
                        text = text.replace("\n", " ")
                        # print ("EXTENT: start:{START}  end:{END}".format(START=start, END=end))
                        event_dict["start"], event_dict["end"], event_dict["arguments"] = start, end, []
                        event_dict["event_type"], event_dict["event_subtype"] = event_type, event_subtype
                        event_dict["event_id"] = event_mention.attrib["ID"]                              
                    elif elem.tag == 'anchor':
                        trigger_start, trigger_end, anchor = elem[0].attrib["START"], elem[0].attrib["END"], elem[0].text
                        anchor = anchor.replace("\n", " ").strip()
                        event_dict["trigger_start"], event_dict["trigger_end"], event_dict["trigger"] = trigger_start, trigger_end, anchor
                        # print ("ANCHOR: start:{START}  end:{END}  anchor:{ANCHOR} ".format(START=start, END=end, ANCHOR=anchor))
                    
                    elif elem.tag == 'event_mention_argument':
                        # print ("event_arguments: ", event_dict["arguments"])
                        role, refid = elem.attrib['ROLE'], elem.attrib["REFID"]
                        event_argument_dict = {}

                        if '-E' in refid:
                            extent_text = argument_dict[refid]["extent_text"].replace("\n", " ")
                            event_argument_dict["extent_start"], event_argument_dict["extent_end"], event_argument_dict["extent"] =\
                                 argument_dict[refid]["extent_start"], argument_dict[refid]["extent_end"], extent_text.strip()
                            event_argument_dict["head_start"], event_argument_dict["head_end"], event_argument_dict["head"] =\
                                 argument_dict[refid]["head_start"], argument_dict[refid]["head_end"], argument_dict[refid]["head_text"].strip()
                            event_argument_dict["type"], event_argument_dict["subtype"], event_argument_dict["role"] =\
                                 argument_dict[refid]["type"],argument_dict[refid]["subtype"],role
                            event_dict["arguments"].append(event_argument_dict)   

                        elif '-V' in refid:
                            extent_text = argument_dict[refid]["extent_text"].replace("\n", " ")
                            event_argument_dict["extent_start"], event_argument_dict["extent_end"], event_argument_dict["extent"] =\
                                 argument_dict[refid]["extent_start"], argument_dict[refid]["extent_end"], extent_text.strip()
                            event_argument_dict["type"], event_argument_dict["subtype"], event_argument_dict["role"] =\
                                 argument_dict[refid]["type"],argument_dict[refid]["subtype"],role
                            event_dict["arguments"].append(event_argument_dict)   

                        elif '-T' in refid:
                            extent_text = argument_dict[refid]["extent_text"].replace("\n", " ")
                            event_argument_dict["extent_start"], event_argument_dict["extent_end"], event_argument_dict["extent"] =\
                                 argument_dict[refid]["extent_start"], argument_dict[refid]["extent_end"], extent_text.strip()
                            event_argument_dict["anchor_dir"], event_argument_dict["val"], event_argument_dict["anchor_val"] =\
                                argument_dict[refid]["anchor_dir"], argument_dict[refid]["val"], argument_dict[refid]["anchor_val"]
                            event_argument_dict["role"] = role
                            event_dict["arguments"].append(event_argument_dict)   

    if event_dict:
        # 最后一次无法进入循环，添加上最后一次的event_mention内容
        event_list.append(event_dict)

    # 将解析后结果写入json文件
    # write_filename = filename[:filename.find(".apf.xml")]
    # with open(json_path + write_filename+".json", "a", encoding='utf-8') as f:
    #     f.write('[')
    #     for i,event_mention in enumerate(event_list):
    #         if i != len(event_list)-1:
    #             f.write(json.dumps(event_mention)+",\n")
    #         else:
    #             f.write(json.dumps(event_mention))
    #     f.write(']')


def load_file(filename):
    # CNN_CF_20030303.1900.02.json
    with open(filename,'r') as load_f:
        load_list = json.load(load_f)
        for event_mention in load_list:
            count = count + len(event_mention["arguments"])
    print ("count: ", count)


# for path in ['D:/ACE/LDC2006T06/data/English/bc/timex2norm/','D:/ACE/LDC2006T06/data/English/bn/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/cts/timex2norm/','D:/ACE/LDC2006T06/data/English/nw/timex2norm/',
#              'D:/ACE/LDC2006T06/data/English/un/timex2norm/','D:/ACE/LDC2006T06/data/English/wl/timex2norm/']:
#     filelist = os.listdir(path)
#     total = len(filelist)
#     for i,filename in enumerate(filelist):
#         print ("{i} / {total} running ...".format(i=(i+1)//4 + 1, total=total//4))
#         if filename.endswith("apf.xml"):
#             apf_filename = path + filename
#             parse_file(filename, apf_filename)
       
# 14,840 sentences + 863 sentences + 672 sentences = 16375 sentences


# parse_file("CNN_CF_20030303.1900.02.apf.xml")
total = 0
filelist = os.listdir("D:/ACE/event_json/")
for filename in filelist:
    with open("D:/ACE/anno_event_json/" + filename, "r", encoding='utf-8') as load_f:
        event_list = json.load(load_f)
        total += len(event_list)
print ("total: ", total)




    