from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Syllabus(BaseModel):
    syllabusName: str
    syllabusId: str

class RelatedDescriptor(BaseModel):
    descriptiveId: str
    descriptor: str

class Book(BaseModel):
    ps: str
    isbn: str

class User(BaseModel):
    userId: str
    firstName: str
    lastName: str

class Tag(BaseModel):
    tagName: str
    tagId: str

class TagType(BaseModel):
    tagTypeId: str
    tags: List[Tag]

class AdditionalInformation(BaseModel):
    Draft_IDs: Optional[str] = None
    Batch: str
    Source: str
    Function_or_Notion: Optional[str] = None
    Example: str
    Anchor: str
    Estimated_Level: Optional[str] = None
    Source_Descriptor: Optional[str] = None
    Communicative_Categories: Optional[str] = None
    N2000_Logit: Optional[str] = None
    Structure: str
    Grammatical_Categories: Optional[str] = None
    Variant_terms: Optional[str] = None
    Notes: str
    Topic_L1: Optional[str] = None

    class Config:
        alias_generator = lambda x: x.replace(" ", "_").replace("/", "_or_")
        populate_by_name = True

class RelatedLOs(BaseModel):
    PL: List = []
    AL: List = []
    GL: List = []
    YL: List = []

class GrammarDescriptor(BaseModel):
    descriptorId: str
    descriptiveId: str
    descriptor: str
    attribution: str
    syllabuses: List[Syllabus]
    relatedDescriptors: List[RelatedDescriptor]
    descriptorStatus: str
    additionalInformation: AdditionalInformation
    tags: List[TagType]
    occupations: List = []
    books: List[Book]
    sdf: List = []
    relatedLOs: RelatedLOs
    status: bool
    created: str
    createdBy: User
    updated: str
    updatedBy: User
    gse: List[TagType]
    grammaticalCategories: List[List[str]]
    businessSkills: List = []
    communicativeCategories: List = []

if __name__ == "__main__":
    # test
    import json
    with open("./raw_data/grammars_data.json", "r") as f:
        for line in f:
            data = json.loads(line)["data"]
            for item in data:
                # print(item["additionalInformation"])
                grammar = GrammarDescriptor(**item)