import json



with open("train.json", "r", encoding='utf-8') as load_f:
    event_list = json.load(load_f)

# write detection labels
# with open("train_detection_labels.txt", "a", encoding='utf-8') as f:
#     for event in event_list:
#         line = event["article_id"] + "\t" + event["event_id"] + "\t" + event["event_type"] + "\t" + event["event_subtype"] + "\t"\
#                             + event["trigger"] + "\t" + str(event["trigger_start"]) + "\t" + str(event["trigger_end"]) + "\n"
#         f.write(line)


with open("train_extraction_labels.txt", "a", encoding='utf-8') as f:

    for event in event_list:
        ini_line = event["article_id"] + "\t" + event["event_id"] + "\t" + event["event_type"] + "\t" + event["event_subtype"] + "\t"\
                                  + event["trigger"] + "\t" + str(event["trigger_start"]) + "\t" + str(event["trigger_end"])
        if event["arguments"]:
            for argument in event["arguments"]:

                line = ini_line + "\t" + argument["role"] + "\t" + argument["extent"] + "\t" + str(argument["extent_start"]) + "\t" + str(argument["extent_end"])

                if "head" in argument:
                    line = line +  argument["head"] + "\t" + argument["head_start"] + "\t" + argument["head_end"] + "\n"
                else:
                    line = line + "\n"
                f.write(line)
        else:
            f.write(ini_line+"\n")

