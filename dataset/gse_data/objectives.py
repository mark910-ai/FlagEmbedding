from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class Syllabus(BaseModel):
    syllabusName: str
    syllabusId: str

class Tag(BaseModel):
    tagName: str
    tagId: str

class TagType(BaseModel):
    tagTypeId: str
    tags: List[Tag]

class Book(BaseModel):
    ps: str
    isbn: str

class SDF(BaseModel):
    sortCompetency: str
    skill: str
    strand: str
    subStrand: str
    competency: str
    development_indicator: str
    diRange: Optional[int] = None

class User(BaseModel):
    userId: str
    firstName: str
    lastName: str

class AdditionalInformation(BaseModel):
    Variant_terms: Optional[str] = None
    Grammatical_Categories: Optional[str] = None
    Structure: Optional[str] = None
    Topic_L1: Optional[str] = None
    YL_simplified_descriptor: Optional[str] = None
    Notes: Optional[str] = None
    Business_Skills: Optional[str] = None
    CEFR_Communicative_activity: Optional[str] = None
    N2000_Logit: Optional[str] = None
    Communicative_Categories: Optional[str] = None
    Source_Descriptor: Optional[str] = None
    Estimated_Level: Optional[str] = None
    Anchor: Optional[str] = None
    Example: Optional[str] = None
    Function_Notion: Optional[str] = None
    Source: Optional[str] = None
    Batch: Optional[str] = None
    Draft_IDs: Optional[str] = None

class RelatedDescriptor(BaseModel):
    descriptiveId: str
    descriptor: str

class Occupation(BaseModel):
    socCode: str
    title: str
    family: str
    descriptors: List[str]

class Objective(BaseModel):
    descriptorId: str
    descriptiveId: str
    descriptor: str
    attribution: str
    syllabuses: List[Syllabus]
    relatedDescriptors: List[RelatedDescriptor]
    descriptorStatus: str
    additionalInformation: AdditionalInformation
    tags: List[TagType]
    occupations: List[Occupation]
    books: List[Book]
    sdf: List[SDF]
    relatedLOs: Dict[str, List[str]]
    di: Optional[str] = None
    status: bool
    created: str
    createdBy: User
    updated: str
    updatedBy: User
    gse: List[TagType]
    grammaticalCategories: List[str]
    businessSkills: List[List[str]]
    communicativeCategories: List[List[str]]

if __name__ == "__main__":
    import json
    with open("./raw_data/objectives_data.json", "r") as f:
        for line in f:
            data = json.loads(line)["data"]
            for item in data:
                # print(item.get("sdf"))
                objective = Objective(**item)
                # print(objective)