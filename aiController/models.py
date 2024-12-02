from transformers import BertTokenizer, BertForSequenceClassification
import torch

model_path = 'aiController/premier_model'

class CarIssueModel:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)

    def predict_causes(self, symptoms):
        inputs = self.tokenizer.encode_plus(symptoms, return_tensors='pt', max_length=512, truncation=True)
        outputs = self.model(**inputs)
        logits = outputs.logits
        top_k = torch.topk(logits, k=3, dim=-1)
        predicted_class_ids = top_k.indices.squeeze().tolist()
        return predicted_class_ids
