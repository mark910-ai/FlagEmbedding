import openai
import pandas as pd
import pydantic
from typing import List
import json
import tqdm
import asyncio
import sys

class Definition(pydantic.BaseModel):
    id: int
    definition: str
    grammaticalCategory: str
    score: float
    example: str
    gse: str
    cefr: str
    knowledge_id: str

class Response(pydantic.BaseModel):
    select_id: int

def get_client() -> openai.AsyncAzureOpenAI:
    client = openai.AsyncAzureOpenAI(
        api_key="34Mgjmn8ZCnACNjHh6VFWrNpetynAiN8", 
        api_version="2024-03-01-preview", 
        azure_endpoint="https://search.bytedance.net/gpt/openapi/online/v2/crawl"
    )
    return client

async def select_meaning(word: str, topic: str, definitions: List[Definition]):
    prompt = f"Here's candidate meanings for the word '{word}':"
    for definition in definitions:
        prompt += f"\n<definition {definition.id}>\n {definition.definition}\n ({definition.grammaticalCategory})\n</definition {definition.id}>\n"
    
    prompt += f"\nNow, please select the most appropriate meaning in the scenario '{topic}' for the word '{word}' from the following knowledge.\n"
    prompt += "If none of them are appropriate, return 0."
    max_tries = 10
    for attempt in range(1, max_tries + 1):
        try:
            response = await get_client().beta.chat.completions.parse(
                model="gpt-4o-mini-2024-07-18",
                messages=[{"role": "user", "content": prompt}],
                response_format=Response
            )
            select = response.choices[0].message.parsed
            if select.select_id == 0:
                return None
            definition = definitions[select.select_id - 1]
            return definition
        except openai.RateLimitError:
            # print("Rate limit error, waiting 10 seconds...")
            await asyncio.sleep(10)
        except:
            if attempt == max_tries:
                return None

async def select_meaning_from_multiple_choices(level: str, word: str, topic: str, definitions: List[Definition]):
    if not definitions:
        return None
    elif len(definitions) == 1:
        meaning = definitions[0]
    else:
        meaning = await select_meaning(word, topic, definitions)
    if meaning is None:
        return None
    js = {
        "level": level,
        "topic": topic,
        "word": word,
        "definition": meaning.definition,
        "grammaticalCategory": meaning.grammaticalCategory,
        "score": meaning.score,
        "example": meaning.example,
        "gse": meaning.gse,
        "cefr": meaning.cefr,
        "knowledge_id": meaning.knowledge_id,
    }
    return js

async def main(suffix_name: str, concurrency: int):
    df = pd.read_csv("../scenario-keywords/temp/word_importance_by_topic_with_definition_{}.csv".format(suffix_name))
    df = df[df["importance"] >= 0]
    df = df[df["definition"].notna()]
    df = df[df["grammaticalCategories"].notna()]
    df = df[df["example"].notna()]
    df = df[df["gse"].notna()]
    df = df[df["cefr"].notna()]
    df = df[df["itemId"].notna()]
    
    # 限制并发数量
    semaphore = asyncio.Semaphore(concurrency)  # 同时最多处理10个请求
    f = open("../scenario-keywords/data/topic_knowledges_{}.jsonl".format(suffix_name), "w")
    
    async def process_and_write(level, topic, word, definitions, score):
        async with semaphore:
            pbar.set_description(f"处理: {word}")
            meaning = await select_meaning_from_multiple_choices(level, word, topic, definitions)
            if meaning is not None:
                f.write(json.dumps(meaning, ensure_ascii=False) + "\n")
            return meaning
    
    tasks = []
    for (level, topic, word), group in df.groupby(["level", "topic", "word"]):
        definitions = []
        for idx, (definition, grammaticalCategory, score, example, gse, cefr, itemId) in enumerate(zip(group["definition"], group["grammaticalCategories"], group["importance"], group["example"], group["gse"], group["cefr"], group["itemId"])):
            definitions.append(Definition(id=idx + 1, definition=definition, grammaticalCategory=",".join(eval(grammaticalCategory)), score=score, example=example, gse=gse, cefr=cefr, knowledge_id=itemId))
        tasks.append(process_and_write(level, topic, word, definitions, group["importance"].iloc[0]))
    
    # 创建进度条
    pbar = tqdm.tqdm(total=len(tasks), desc="处理进度")
    
    # 修改处理函数以更新进度条
    async def process_with_progress(task):
        result = await task
        pbar.update(1)  # 更新进度
        return result
    
    results = await asyncio.gather(*(process_with_progress(task) for task in tasks))
    
    pbar.close()
    
    f.close()  # 关闭文件

if __name__ == "__main__":
    suffix_name = sys.argv[1]
    concurrency = sys.argv[2]
    asyncio.run(main(suffix_name, int(concurrency)))
        