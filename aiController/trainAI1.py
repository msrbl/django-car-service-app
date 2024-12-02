from sklearn.preprocessing import MultiLabelBinarizer
import torch
from transformers import BertTokenizer, BertModel, BertConfig
from torch import nn
from torch.utils.data import Dataset
from transformers import Trainer, TrainingArguments, TrainerCallback
from sklearn.metrics import accuracy_score, classification_report
import json
import os

class CarIssueDataset(Dataset):
    def __init__(self, tokenizer, data, max_len=512):
        self.tokenizer = tokenizer
        self.data = data
        self.max_len = max_len
        self.label_encoder = MultiLabelBinarizer(classes=[i for i in range(50)])

        self.labels = self.label_encoder.fit_transform([item['causes'] for item in data])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        input_text = item['symptoms']
        labels = self.labels[index]

        inputs = self.tokenizer(input_text, max_length=self.max_len, padding='max_length', truncation=True, return_tensors="pt")

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': torch.tensor(labels, dtype=torch.float32)
        }

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: file '{file_path}' does not exist.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error: file isn't in JSON format.")
        return None

    if not isinstance(data, dict) or 'symptoms' not in data or 'causes' not in data:
        print("Error: invalid data structure. Expected 'symptoms' and 'causes' fields.")
        return None

    if not isinstance(data['symptoms'], str):
        print("Error: field 'symptoms' must be string.")
        return None

    if not isinstance(data['causes'], list) or len(data['causes']) != 2 or not all(isinstance(i, int) for i in data['causes']):
        print("Error: field 'causes' must be List with length 2.")
        return None

    return data

def compute_metrics(p):
    preds = (p.predictions > 0.5).astype(int)
    labels = p.label_ids
    accuracy = accuracy_score(labels, preds)
    report = classification_report(labels, preds, output_dict=True, zero_division=0)
    return {
        'accuracy': accuracy,
        'precision': report['weighted avg']['precision'],
        'recall': report['weighted avg']['recall'],
        'f1': report['weighted avg']['f1-score']
    }

class CustomBertForMultiLabelClassification(nn.Module):
    def __init__(self, model_name, num_labels):
        super(CustomBertForMultiLabelClassification, self).__init__()
        self.bert = BertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)
    
    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        loss = None
        if labels is not None:
            loss_fn = nn.BCEWithLogitsLoss()
            loss = loss_fn(logits, labels)
        
        return {"loss": loss, "logits": logits}

model_name = 'bert-base-uncased'
num_labels = 50
tokenizer = BertTokenizer.from_pretrained(model_name)
model = CustomBertForMultiLabelClassification(model_name, num_labels)

data_file = 'traindataset.json'
data = load_data(data_file)
dataset = CarIssueDataset(tokenizer, data)

train_size = int(0.8 * len(data))
train_dataset = CarIssueDataset(tokenizer, data[:train_size])
eval_dataset = CarIssueDataset(tokenizer, data[train_size:])

class LoggingCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        _ = logs.pop("total_flos", None)
        if state.is_local_process_zero:
            print(logs)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=5,
    per_device_train_batch_size=12,
    per_device_eval_batch_size=12,
    warmup_steps=10,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    save_steps=10_000,
    save_total_limit=2,
    learning_rate=1e-5,
    load_best_model_at_end=True,
    eval_strategy="epoch",
    save_strategy="epoch",
    fp16=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    callbacks=[LoggingCallback]
)

trainer.train()

model.save_pretrained('./premier_model')
tokenizer.save_pretrained('./premier_model')