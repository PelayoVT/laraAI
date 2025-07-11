from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model
import torch

model_name = "mistralai/Mistral-7B-v0.3"
dataset_path = "datasets/datasetclinico_ansiedad.jsonl"
output_dir = "outputs/modelo_clinico_lora"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  

def tokenize_chat(example):
    text = ""
    for message in example["messages"]:
        role = message["role"]
        content = message["content"].strip()
        if role == "user":
            text += "<|user|>\n" + content + "\n"
        elif role == "assistant":
            text += "<|assistant|>\n" + content + "\n"

    encoding = tokenizer(
        text,
        truncation=True,
        padding=False,  
        max_length=1024
    )

    return {
        "input_ids": encoding["input_ids"],
        "attention_mask": encoding["attention_mask"],
        "labels": encoding["input_ids"][:]  
    }

dataset = load_dataset("json", data_files=dataset_path, split="train")
tokenized_dataset = dataset.map(tokenize_chat, remove_columns=["messages"])

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True,
    return_tensors="pt"
)

training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=6,
    gradient_accumulation_steps=2,
    learning_rate=1e-5,
    num_train_epochs=3,
    max_steps=1500,
    warmup_steps=100,
    logging_dir="./logs",
    logging_steps=10,
    save_strategy="steps",
    save_steps=250,
    fp16=True,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator
)

trainer.train()
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)


