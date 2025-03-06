from collections import defaultdict
from typing import List, Union
from vocab_item import Item, Topic, Region
import json

class VocabSearcher:
    def __init__(self, data: List[Item]):
        self.data = data
        self.index = defaultdict(list)
        self._build_index()
    
    def _build_index(self):
        for item in self.data:
            item: Item
            self.index[item.expression.lower()].append(item)
            if item.variants:
                for variant in item.variants:
                    self.index[variant.variant.lower()].append(item)
            if item.region:
                for region_variant in item.region.variants:
                    for variant in region_variant.variants:
                        self.index[variant.variant.lower()].append(item)

    def search(self, expression: str) -> Union[List[Item], None]:
        return self.index.get(expression, None)
    
    @classmethod
    def from_jsonl(cls, path: str) -> 'VocabSearcher':
        with open(path, "r") as f:
            data = [Item.model_validate(json.loads(line)) for line in f]
        return cls(data)
