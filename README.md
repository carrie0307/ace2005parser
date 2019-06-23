# ACE2005事件抽取数据预处理

ACE2005事件抽取数据预处理工作是指，根据原始的.apf.xml和.sgm文件，提取与事件有关的要素(sentence,trigger,argument及trigger和argument在原文中的offset)，并通过StandfordCoreNLP对sentence进行词性和句法依赖解析，根据.apf.xml文件中的entity、value和timex2对句子进行"BIO"的类型标注，最终将结果以json形式写入。

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

### 数据样例

见./example/目录下

## 其他说明

之前有使用[ace-data-prep](https://github.com/mgormley/ace-data-prep/)进行预处理，但根据处理结果观察，得到的是用于关系抽取的预处理结果，数据中不包含事件抽取相关要素信息。处理过程记录见https://blog.csdn.net/carrie_0307/article/details/91128013


## TO DO

1. 列出train/dev/test的数据列表

2. 将trigger identification, argument identification和argument classification的"labels"整理出来


---

以上是数据处理过程，欢迎大家使用，如有问题请与我联系747100368@qq.com。

事件总量: 5349

2019.06.21