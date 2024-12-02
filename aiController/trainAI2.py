import os
import json
import torch
import datetime
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch import nn
import numpy as np
from torch.utils.tensorboard import SummaryWriter

class CarIssueDataset(Dataset):
    def __init__(self, tokenizer, data, max_len=512, num_labels=50):
        self.tokenizer = tokenizer
        self.data = data
        self.max_len = max_len
        self.label_encoder = MultiLabelBinarizer(classes=[i for i in range(num_labels)])
        self.labels = self.label_encoder.fit_transform([item['causes'] for item in data])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        input_text = item['symptoms']
        labels = self.labels[index]
        inputs = self.tokenizer(
            input_text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': torch.tensor(labels, dtype=torch.float32)
        }

def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for entry in data:
            if not isinstance(entry.get("symptoms"), str) or not isinstance(entry.get("causes"), list) or len(entry["causes"]) != 2:
                raise ValueError("Incorrect data structure")
        return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return None
    except ValueError as ve:
        print(ve)
        return None

def compute_metrics(p):
    preds = torch.sigmoid(torch.tensor(p.predictions)).cpu().numpy()
    labels = p.label_ids

    preds = (preds > 0.2).astype(int)
    print("\n")
    print(f"Predictions shape: {preds.shape}, Labels shape: {labels.shape}")

    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='samples', zero_division=0)

    print("\n")
    print("Predicted positives per label:", preds.sum(axis=0))
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def save_model_and_tokenizer(model, tokenizer, model_dir="model\\models"):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    model_dir = model_dir + "\\" + current_time
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    print("Model and tokenizer saved to", model_dir)

data = load_data("traindataset.json")


def train_model(data_file, model_dir="model", epochs=20, batch_size=4, learning_rate=1e-5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    data = load_data(data_file)
    if data is None:
        return

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    train_data, eval_data = train_test_split(data, test_size=0.2)

    train_dataset = CarIssueDataset(tokenizer, train_data)
    eval_dataset = CarIssueDataset(tokenizer, eval_data)

    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=50)
    model.classifier = nn.Linear(model.config.hidden_size, 50)
    model.config.problem_type = "multi_label_classification"
    model.to(device)

    training_args = TrainingArguments(
        output_dir=model_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        logging_dir=f"{model_dir}/logs",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        fp16=torch.cuda.is_available()
    )

    writer = SummaryWriter(log_dir=f"{model_dir}/tensorboard_logs")

    class CustomTrainer(Trainer):
        def log(self, logs):
            super().log(logs)
            for key, value in logs.items():
                writer.add_scalar(key, value, self.state.global_step)
            writer.flush()

    print("Sample train labels:", train_dataset[0]['labels'])
    print("Sample eval labels:", eval_dataset[0]['labels'])

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer
    )

    trainer.train()
    save_model_and_tokenizer(model, tokenizer, model_dir=model_dir)
    writer.close()

train_model("traindataset.json")
