import json
from vocab_item import Item
from objectives import Objective
from grammar import GrammarDescriptor

if __name__ == "__main__":
    data = []
    with open("raw_data/vocabulary_data.json", "r") as f:
        for line in f:
            js = json.loads(line)
            for item in js['data']:
                # print(json.dumps(item, ensure_ascii=False))
                data.append(Item.model_validate(item))

    with open("data/vocabulary_data.jsonl", "w") as f:
        for item in data:
            f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
    
    print(f"Saved {len(data)} items to data/vocabulary_data.jsonl")

    with open("raw_data/objectives_data.json", "r") as f:
        for line in f:
            js = json.loads(line)
            for item in js['data']:
                data.append(Objective.model_validate(item))

    with open("data/objectives_data.jsonl", "w") as f:
        for item in data:
            f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
    print(f"Saved {len(data)} items to data/objectives_data.jsonl")

    with open("raw_data/grammars_data.json", "r") as f:
        for line in f:
            js = json.loads(line)
            for item in js['data']:
                data.append(GrammarDescriptor.model_validate(item))

    with open("data/grammar_data.jsonl", "w") as f:
        for item in data:
            f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
    print(f"Saved {len(data)} items to data/grammar_data.jsonl")
