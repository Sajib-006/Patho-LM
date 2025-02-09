import argparse
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, balanced_accuracy_score, roc_auc_score, confusion_matrix
from utils import fasta_to_df

def compute_metrics(logits, labels):
    predictions = np.argmax(logits, axis=1)
    labels = np.array(labels, dtype=int)
    predictions = np.array(predictions, dtype=int)
    
    acc = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    mcc = matthews_corrcoef(labels, predictions)
    balanced_acc = balanced_accuracy_score(labels, predictions)
    auc_roc = None
    
    if len(np.unique(labels)) == 2:
        probs = np.exp(logits[:, 1]) / np.sum(np.exp(logits), axis=1)
        auc_roc = roc_auc_score(labels, probs)
    
    cm = confusion_matrix(labels, predictions)
    return {
        'accuracy': acc,
        'f1_score': f1,
        'mcc': mcc,
        'auc_roc': auc_roc,
        'balanced_accuracy': balanced_acc,
        'confusion_matrix': cm.tolist()
    }

def encode_sequence(sequence, tokenizer, max_length):
    return tokenizer(sequence, truncation=True, padding='max_length', max_length=max_length, return_tensors='pt')

def evaluate(model_path, test_file=None, sequence=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(model_path, ignore_mismatched_sizes=True).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    if sequence:
        inputs = encode_sequence(sequence, tokenizer, tokenizer.model_max_length)
        with torch.no_grad():
            outputs = model(**{k: v.to(device) for k, v in inputs.items()})
        logits = outputs.logits.cpu().numpy()
        print("Single Sequence Prediction:", np.argmax(logits, axis=1))
        return
    
    test_df = fasta_to_df(test_file)
    label_map = {
        'non-pathogen': 0,
        'pathogen': 1  
    }
    test_df['label'] = test_df['label'].str.lower().map(label_map)
    dataset = Dataset.from_pandas(test_df)
    dataset = dataset.map(lambda x: encode_sequence(x['sequence'], tokenizer, tokenizer.model_max_length), batched=True)
    dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])

    dataloader = torch.utils.data.DataLoader(dataset, batch_size=8)
    logits_list, labels_list = [], []
    
    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            inputs = {k: v.to(device) for k, v in batch.items() if k != 'label'}
            # print(type(batch['label']), batch['label'])
            labels = np.array(batch['label'])
            outputs = model(**inputs)
            logits_list.append(outputs.logits.cpu().numpy())
            labels_list.append(labels)
    
    logits = np.concatenate(logits_list, axis=0)
    labels = np.concatenate(labels_list, axis=0)
    results = compute_metrics(logits, labels)
    print("Evaluation Metrics:", results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to the fine-tuned model directory")
    parser.add_argument("--test_file", type=str, help="Path to the test fasta file")
    parser.add_argument("--sequence", type=str, help="Single DNA sequence to classify")
    args = parser.parse_args()
    evaluate(args.model_path, args.test_file, args.sequence)
