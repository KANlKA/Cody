import json, collections, random
rows = [json.loads(l) for l in open("space_artifacts/serving_chunks.jsonl", encoding="utf-8")]
print(collections.Counter(r["language"] for r in rows))
random.seed(1)
en = [r for r in rows if r["language"] == "en"]
for r in random.sample(en, 5):
    print("-", r["text"][:300], "\n")