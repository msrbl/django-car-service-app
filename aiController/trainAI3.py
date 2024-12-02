from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
import torch
import json
import pandas as pd
import numpy as np


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
    
# Данные с текстовыми метками
data = load_data("traindataset.json")

df = pd.DataFrame(data)

# Словарь для текстовых меток
unique_labels = sorted(set(label for item in data for label in item["causes"]))
label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
id_to_label = {idx: label for label, idx in label_to_id.items()}

# Инициализация токенайзера
tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

# Кодирование данных
def encode_data(example):
    tokenized = tokenizer(example["symptoms"], truncation=True, padding="max_length", max_length=128)
    label_vector = [1 if label in example["causes"] else 0 for label in unique_labels]
    tokenized["labels"] = torch.tensor(label_vector, dtype=torch.float32)  # Для BCEWithLogitsLoss
    return tokenized

encoded_data = [encode_data(row) for row in data]
train_data, val_data = train_test_split(encoded_data, test_size=0.2)

# Датасет
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {key: torch.tensor(val) if isinstance(val, list) else val for key, val in self.data[idx].items()}

train_dataset = CustomDataset(train_data)
val_dataset = CustomDataset(val_data)

# Коллектор данных
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Загрузка модели
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=len(unique_labels),
    problem_type="multi_label_classification"  # Указание multi-label задачи
)

# Настройки обучения
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    logging_dir='./logs',  # Для TensorBoard
    logging_steps=50,
)

# Подсчет метрик
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = (torch.sigmoid(torch.tensor(logits)) > 0.5).int()

    unique_labels = np.unique(labels)
    try:
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="weighted", zero_division=0
        )
        if len(unique_labels) > 1:
            roc_auc = roc_auc_score(labels, logits, average="weighted", multi_class="ovr")
        else:
            roc_auc = 0
    except ValueError: 
        precision, recall, f1, roc_auc = 0, 0, 0, 0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
    }

# Тренировка
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()
trainer.save_model("./trained_model")

# Анализ результатов
predictions = trainer.predict(val_dataset)
logits = torch.sigmoid(torch.tensor(predictions.predictions))
decoded_preds = [[id_to_label[idx] for idx, val in enumerate(pred) if val > 0.5] for pred in logits]
for i, pred in enumerate(decoded_preds):
    print(f"Пример {i + 1}: Предсказанные причины: {', '.join(pred)}")