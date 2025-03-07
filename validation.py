import json
import random
from typing import Dict, List


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

def inference(data: List[Dict]):
    from FlagEmbedding import BGEM3FlagModel

    model_path = '/content/drive/MyDrive/DSSM/encoder_only_m3_bge-m3_sd/checkpoint-10000'

    model = BGEM3FlagModel(model_path,
                        use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

    sentences_1 = [item['query'] for item in data]
    sentences_2 = [item['document'] for item in data]

    embeddings_1 = model.encode(sentences_1,
                                batch_size=12,
                                max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
                                )['dense_vecs']
    embeddings_2 = model.encode(sentences_2)['dense_vecs']
    similarity = embeddings_1 @ embeddings_2.T
    # Get diagonal elements which represent similarities between corresponding pairs
    similarity_scores = similarity.diagonal()
    return similarity_scores

def main():
    import random
    data = load_jsonl('dataset/gse_train_data/training_data_all_distill.jsonl')
    print(len(data))
    # shuffle data
    random.shuffle(data)
    data = data[:100]
    similarity = inference(data)
    threshold = 0.5
    # compare similarity with label and print the accuracy
    # also print the false positive and false negative, and the precision and recall
    precision = 0
    recall = 0
    false_positive = 0
    false_negative = 0
    correct = 0
    for i, item in enumerate(data):
        if similarity[i] > threshold and item['label'] == 1:
            correct += 1
        elif similarity[i] <= threshold and item['label'] == 0:
            correct += 1
        elif similarity[i] > threshold and item['label'] == 0:
            false_positive += 1
        elif similarity[i] <= threshold and item['label'] == 1:
            false_negative += 1
    precision = correct / (correct + false_positive)
    recall = correct / (correct + false_negative)
    print(f'Accuracy: {correct / len(data)}')
    print(f'False Positive: {false_positive}')
    print(f'False Negative: {false_negative}')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')

if __name__ == '__main__':
    main()
