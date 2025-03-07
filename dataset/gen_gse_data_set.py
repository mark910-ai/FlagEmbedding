import json
import random
from typing import List, Dict
import re

def load_jsonl(file_path: str, limit: int = None) -> List[Dict]:
    """
    load jsonl file
    Args:
        file_path: jsonl file path
        limit: limit the number of lines to read, default is None to read all
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line.strip():
                data.append(json.loads(line))
                if limit and i >= limit - 1:
                    break
    return data

def create_document(item: Dict) -> str:
    """
    create document string
    """
    doc = {
        "expression": item["expression"],
        "definition": item["definition"],
        "cefr": item["cefr"],
        "grammaticalCategories": item["grammaticalCategories"],
    }
    return json.dumps(doc, ensure_ascii=False)

def contains_word(sentence: str, word: str) -> bool:
    """
    check if sentence contains specified word (consider word boundaries)
    """
    if not sentence or not word:
        return False
    pattern = r'\b' + re.escape(word) + r'\b'
    return bool(re.search(pattern, sentence, re.IGNORECASE))

def find_soft_negative(item: Dict, data: List[Dict]) -> Dict:
    """
    find other data with the same expression as the original data as soft negative data
    """
    for other_item in data:
        if (other_item["itemId"] != item["itemId"] and 
            other_item["expression"] == item["expression"] and 
            other_item["grammaticalCategories"] != item["grammaticalCategories"]):
            return other_item
    return None

def generate_training_data(data: List[Dict], output_path1: str):
    """
    generate training data set with memory-efficient processing
    """
    prompt = "Given an english sentence and a word explanation, determine if the word explanation is correct or not."
    type = "symmetric_class"
    
    total_count = len(data)
    processed_count = 0
    complete_count = 0
    
    print(f"start processing, total {total_count} source data")
    
    # Open file for writing immediately to avoid storing everything in memory
    with open(output_path1, 'w', encoding='utf-8') as f:
        # Process one item at a time
        for item in data:
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"processed: {processed_count}/{total_count} data, complete data: {complete_count} data")
                
            if not item.get("example"):
                continue
                
            # Reset lists for each iteration to avoid memory accumulation
            positive_data = []
            negative_data = []
            
            # Generate positive data
            positive_data.append(f"The word {item['expression']} is a {item['grammaticalCategories']} and its definition is: {item['definition']}.")

            # Generate negative data - only get one at a time
            # negative_item = None
            # for _ in range(10):  # Limit attempts to find negative sample
            #     candidate = random.choice(data)
            #     if (candidate["itemId"] != item["itemId"] and 
            #         not contains_word(item["example"], candidate["expression"])):
            #         negative_item = candidate
            #         break
            
            # if negative_item:
            #     negative_data.append(f"The word {negative_item['expression']} is a {negative_item['grammaticalCategories']} and its definition is: {negative_item['definition']}.")
            
            # Find soft negative - don't store full list
            soft_negative_item = find_soft_negative(item, data)
            if soft_negative_item:
                negative_data.append(f"The word {soft_negative_item['expression']} is a {soft_negative_item['grammaticalCategories']} and its definition is: {soft_negative_item['definition']}.")
                complete_count += 1

            # Write immediately instead of accumulating
            if positive_data and negative_data:
                training_sample = {
                    "query": f"In the sentence: {item['example']} What is the meaning of the word: {item['expression']}?",
                    "pos": positive_data,
                    "neg": negative_data,
                    "prompt": prompt,
                    "type": type
                }
                f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
                
            # Clear references to help garbage collection
            positive_data = None
            negative_data = None
    
    # Print final statistics
    print("\nprocessing completed!")
    print(f"source data total: {total_count}")
    print(f"processed data statistics:")
    print(f"- all data set ({output_path1}): {processed_count} data")
    print(f"- complete data with soft negative: {complete_count} data")

def main():
    # input and output file path
    input_path = "dataset/gse_data/data/vocabulary_data.jsonl"
    output_path1 = "dataset/gse_train_data/data/training_data_all.jsonl"
    # output_path2 = "data/gse_train_data/data/training_data_complete.jsonl"
    
    # load data (limit 50 lines)
    data = load_jsonl(input_path)
    
    # generate two types of training data
    generate_training_data(data, output_path1)

def gen_validation_data_set_from_distil_data(input_path: str, output_path: str):
    """
    generate validation data set from distil data

    Args:
        input_path: distil data path
        output_path: output data path
    
    Input Example:
    {"query": "It was bustling with people buying fresh produce.", "document": {"expression": "it", "definition": "used to refer to something that has already been mentioned", "cefr": "<A1 (10-21)"}, "label": 1}

    Output Example:
    {"query": "In this sentence: It was bustling with people buying fresh produce. What is the meaning of the word: it?", "document": "The word it is a pronoun and its definition is: used to refer to something that has already been mentioned.", "label": 1}
    """
    data = load_jsonl(input_path)
    total_count = len(data)
    processed_count = 0
    complete_count = 0

    # Open file for writing immediately to avoid storing everything in memory
    with open(output_path, 'w', encoding='utf-8') as f:
        # Process one item at a time
        for item in data:
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"processed: {processed_count}/{total_count} data, complete data: {complete_count} data")
            
            expression = item["document"]["expression"]
            if expression in item["query"]:
                f.write(json.dumps({
                    "query": f"In this sentence: {item['query']}, what is the meaning of the word: {expression}?",
                    "document": f"The word {expression} definition is: {item['document']['definition']}.",
                    "label": item["label"]
                }, ensure_ascii=False) + '\n')
                complete_count += 1

    print("\nprocessing completed!")
    print(f"source data total: {total_count}")
    print(f"processed data statistics:")
    print(f"- all data set ({output_path}): {processed_count} data")
    print(f"- complete data with soft negative: {complete_count} data")
                
                

if __name__ == "__main__":
    try:
        main()
        # input_path = "data/gse_train_data/data/training_data_all_distill.jsonl"
        # output_path = "data/gse_train_data/data/validation_data.jsonl"
        # gen_validation_data_set_from_distil_data(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
