from typing import List, Optional, Iterator
from pydantic import BaseModel, RootModel, Field

class AudioFiles(BaseModel):
    bre: Optional[str] = None
    ame: Optional[str] = None

class TopicLevel(BaseModel):
    id: Optional[str] = None
    level: str
    description: str

class Topic(RootModel):
    root: List[List[TopicLevel]]

class Variant(BaseModel):
    audioFiles: Optional[AudioFiles] = None
    variant: Optional[str] = None

class RegionVariant(BaseModel):
    variants: List[Variant]
    label: Optional[str] = None

class RegionVariants(RootModel):
    root: List[RegionVariant] = Field(alias="__root__")
    def __iter__(self) -> Iterator[RegionVariant]:
        return iter(self.root)

    def __getitem__(self, item) -> RegionVariant:
        return self.root[item]

class Region(BaseModel):
    label: str
    note: str
    variants: RegionVariants

class Item(BaseModel):
    itemId: str
    expression: str
    audioFiles: Optional[AudioFiles] = None
    variants: Optional[List[Variant]] = None
    thesaurus: str
    definition: str
    example: str
    audience: str
    cefr: str
    gse: str
    grammaticalCategories: List[str]
    collos: List[str]
    topics: Topic
    region: Region
    expression_bre: Optional[str] = None

    def to_simple_item(self) -> 'SimpleItem':
        return SimpleItem(
            expression=self.expression,
            definition=self.definition,
            example=self.example,
            cefr=self.cefr,
            gse=self.gse,
            grammaticalCategories=self.grammaticalCategories,
            itemId=self.itemId,
        )

class SimpleItem(BaseModel):
    expression: str
    definition: str
    example: str
    cefr: str
    gse: str
    grammaticalCategories: List[str]
    itemId: str

def unitest():
    import json
    js = json.loads('''{
            "itemId": "ua8444abd28d0e715.-5299d1a3.145b71306a8.-4b87",
            "expression": "colour",
            "audioFiles": {
                "bre": "https://www.english.com/t4qgNJUYH866vT43/gsettk/ttk/audio/bre_brelasdecolour.mp3",
                "ame": "https://www.english.com/t4qgNJUYH866vT43/gsettk/ttk/audio/ame_color1.mp3"
            },
            "thesaurus": "",
            "definition": "if something has colour, it has bright colours and looks nice",
            "example": "flowers that will add colour to your garden",
            "audience": "GL",
            "cefr": "A1 (22-29)",
            "gse": "27",
            "grammaticalCategories": [
                "noun"
            ],
            "collos": [],
            "variants": [],
            "topics": [
                [
                    {
                        "id": "383",
                        "level": "1",
                        "description": "Physical attributes"
                    },
                    {
                        "description": "Colour",
                        "level": "2",
                        "id": "386"
                    },
                    {
                        "level": "3",
                        "description": "Talking about colour",
                        "id": "388"
                    }
                ]
            ],
            "region": {
                "label": "BrE",
                "note": "",
                "variants": [
                    {
                        "variants": [
                            {
                                "audioFiles": {
                                    "bre": null,
                                    "ame": null
                                },
                                "variant": "color"
                            }
                        ],
                        "label": "AmE"
                    }
                ]
            }
        }''')
    item = Item.model_validate(js)
    return item

if __name__ == "__main__":
    item = unitest()
