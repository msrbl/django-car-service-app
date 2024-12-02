import json

with open("./premier/aiController/prepare_dataset/traindataset.json", "r", encoding="utf-8") as f1:
    symptoms = json.load(f1)

with open("./premier/aiController/prepare_dataset/causes.json", "r", encoding="utf-8") as f2:
    causes = json.load(f2)

for row in symptoms:
    row["causes"] = [causes.get(str(cause), f"Unknown cause: {cause}") for cause in row["causes"]]

with open("./premier/aiController/trandataset_out.json", 'w', encoding='utf-8') as output_file:
        json.dump(symptoms, output_file, ensure_ascii=False, indent=4)