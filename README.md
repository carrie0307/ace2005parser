# ACE2005事件抽取数据预处理

* **补充说明: 这份代码只处理了ACE05语料中含有事件的句子，而这在具体的论文实验中是错误的，应当使用全量数据，在此说明。**

ACE2005事件抽取数据预处理工作是指，根据原始的.apf.xml和.sgm文件，提取与事件有关的要素(sentence,trigger,argument及trigger和argument在原文中的offset)，并通过StandfordCoreNLP对sentence进行词性和句法依赖解析，根据.apf.xml文件中的entity、value和timex2对句子进行"BIO"的类型标注，最终将结果以json形式写入。

[2019.08.02更]add_bio.py存在的一个小bug:对于一些entity/time/value都不包含的句子，将会出现没有bio的情况(其他正常的提取没有问题)。这里代码不改了，后续添加吧(例如:un/rec.arts.mystery_20050219.1126)

## 代码说明

### requirements

* xml.etree.cElementTree
* stanfordcorenlp
* tokenize

* standforcoeNLP模型下载地址

https://stanfordnlp.github.io/CoreNLP/history.html



### parse.py

从xml文件中提取事件要素信息，存入./event_json

### std_parse.py

结合./event_json和.apf.xml文件，首先使用NLTK进行分句，然后用StandfordCorNLP进行必要的标注并计算每个token相对全文的offset, 结果写入./anno_event_json


### add_bio.py

给./anno_event_json中的标注结果添加上BIO标注信息(根据.apf.xml中的entity,value和time进行BIO标注), 结果写入./anno_event_json_final/目录下。

注意，部分sentence中不包括LDC所标注的entity/value/time,因此这些sentence的字典中没有'bio'一项，例如
```
{"article_id":"AFP_ENG_20030304.0250",
"event_id":"AFP_ENG_20030304.0250-EV5-1",
"event_type":"Conflict",
"event_subtype":"Attack",
"sentence_id":-7493870223321462845,
"sentence":"There were no reports of injuries in the second blast.",
"sentence_start":862,
"sentence_end":916,
"tokens":["There", "were", "no", "reports", "of", "injuries", "in", "the", "second", "blast", "."],
"pos":[["There", "EX"], ["were", "VBD"], ["no", "DT"], ["reports", "NNS"], ["of", "IN"], ["injuries", "NNS"], ["in", "IN"], ["the", "DT"], ["second", "JJ"], ["blast", "NN"], [".", "."]],
"ner":[["There", "O"], ["were", "O"], ["no", "O"], ["reports", "O"], ["of", "O"], ["injuries", "O"], ["in", "O"], ["the", "O"], ["second", "ORDINAL"], ["blast", "O"], [".", "O"]],
"dependency":[["ROOT", 0, 2], ["expl", 2, 1], ["neg", 4, 3], ["nsubj", 2, 4], ["case", 6, 5], ["nmod", 4, 6], ["case", 10, 7], ["det", 10, 8], ["amod", 10, 9], ["nmod", 2, 10], ["punct", 2, 11]],
"trigger":"blast",
"trigger_start":"910",
"trigger_end":"914",
"arguments":[],
"tokens_offset":[[862, 866], [868, 871], [873, 874], [876, 882], [884, 885], [887, 894], [896, 897], [899, 901], [903, 908], [910, 914], [915, 915]]}
```

### 数据样例

见./example/目录下

## 其他说明

之前有使用[ace-data-prep](https://github.com/mgormley/ace-data-prep/)进行预处理，但根据处理结果观察，得到的是用于关系抽取的预处理结果，数据中不包含事件抽取相关要素信息。处理过程记录见https://blog.csdn.net/carrie_0307/article/details/91128013


## TO DO

1. 列出train/dev/test的数据列表

2. 将trigger identification, argument identification和argument classification的"labels"整理出来


---

以上是数据处理过程，欢迎大家使用。

事件总量: 5349

2019.06.21
