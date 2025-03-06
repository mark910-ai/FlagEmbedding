import pandas as pd
from vocab_searcher import VocabSearcher
from typing import List
from vocab_item import Item
import re
import sys

def load_topic_vocab_relation(path: str):
    with open(path, "r") as f:
        data = []
        for line in f:
            level_topic, word, impotance = line.strip().split("\t")
            level, topic = level_topic.split("-", 1)
            data.append((level, topic, word, impotance))
    return data

def gse_score_extract(score: str):
    # get lower and upper score
    m = re.match(r"^.*\(([0-9]+-[0-9]+)\).*$", score)
    if m:
        range = m.groups()[0]
        lower, upper =  range.split("-")
        lower, upper = int(lower), int(upper)
    else:
        raise ValueError(f"Invalid score: {score}")
    return lower, upper

    # ['A1 (22-29)', '<A1 (10-21)', '<A1 (10-21)*', 'A1 (22-29)*',
    #    'A2+ (36-42)*', 'A2 (30-35)', 'A2+ (36-42)', 'A2 (30-35)*',
    #    'B1+ (51-58)', 'B1 (43-50)', 'B1 (43-50)*', 'B1+ (51-58)*',
    #    'B2 (59-66)', 'B2+ (67-75)', 'B2 (59-66)*']


def is_qualified_item(items: List[Item], word_level: str) -> List[Item]:
    # find cloeset level    
    level_mapping = {
        # A1 (22-29)
            # <A1 (10-21)
            "A1": (0, 29),
            # "A2": (30, 35),
            # "A2+": (36, 42),
            "A2": (30, 42),
            "B1": (43, 50),
            "B1+": (51, 58),
            "B2": (59, 75),           
        }
    lower, upper = level_mapping[word_level]
    def get_gse_score(item: Item) -> int:
        try:
            return int(item.gse.strip("*"))
        except ValueError:
            print(f"Invalid GSE score: {item.gse}")
            return None
    qualified_items = []
    near_items = []
    for item in items:
        gse_score = get_gse_score(item)
        if not gse_score:
            continue
        if lower <= gse_score <= upper:
            qualified_items.append(item)
        else: # find closest level
            if min(abs(gse_score - lower), abs(gse_score - upper)) <= 10:
                near_items.append(item)
                
    return qualified_items + near_items

if __name__ == "__main__":
    suffix_name = sys.argv[1]
    data = load_topic_vocab_relation("../scenario-keywords/temp/word_importance_by_topic_{}.txt".format(suffix_name))
    df = pd.DataFrame(data, columns=["level", "topic", "word", "importance"])
    searcher = VocabSearcher.from_jsonl("../gse_data/data/vocabulary_data.jsonl")
    output = []
    for _, group in df.groupby(["level", "topic"]):
        for _, row in group.iterrows():
            # if float(row["importance"]) <= 0:
            #     continue
            row_proto = row.to_dict()
            word_level = row["level"]
            items = searcher.search(row["word"])
            if not items:
                output.append(row_proto)
                continue
            knowldeges = []
            near_items = is_qualified_item(items, word_level)
            for item in near_items:
                simple_item = item.to_simple_item()
                new_row = row_proto.copy()
                new_row.update(simple_item.model_dump())
                knowldeges.append(new_row)
            if len(knowldeges) > 0:
                output.extend(knowldeges)
            else:
                output.append(row_proto)
    df = pd.DataFrame(output)
    df.to_csv("../scenario-keywords/temp/word_importance_by_topic_with_definition_{}.csv".format(suffix_name), index=False)

