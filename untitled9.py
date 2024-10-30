# -*- coding: utf-8 -*-
"""Untitled9.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JwbUNg3kwUJauo994XTt_e20kfNLWMf9
"""

import os
os.environ["WANDB_DISABLED"] = "true"

import torch
from trl import SFTTrainer
from datasets import load_dataset, DatasetDict
from transformers import TrainingArguments, TextStreamer
from unsloth import FastLanguageModel, is_bfloat16_supported

# Define model and training parameters
max_seq_length = 1024
dtype = None
load_in_4bit = True

# Load pre-trained model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# Apply LoRA configurations (without merging)
model = FastLanguageModel.get_peft_model(
    model,
    r=8,
    lora_alpha=16,
    lora_dropout=0,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Define the prompt format for the task
career_prompt = """Given the individual's profile:
{input}

Recommend a suitable career path and explain why.

Response: {output}"""

# Function to format dataset prompts
def format_prompts(examples):
    formatted = []
    for input_data, output in zip(examples["Input"], examples["Output"]):
        text = career_prompt.format(
            input=input_data,
            output=output
        )
        formatted.append(text)
    return {"text": formatted}

# Load datasets and format prompts
train_dataset = load_dataset("csv", data_files="train dataset llama.csv", split="train")
train_dataset = train_dataset.map(format_prompts, batched=True)

test_dataset = load_dataset("csv", data_files="new.csv", split="train")
test_dataset = test_dataset.map(format_prompts, batched=True)

# Training arguments with checkpointing every 10 steps
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    warmup_ratio=0.03,
    max_steps=100,
    learning_rate=1e-4,
    fp16=not is_bfloat16_supported(),
    bf16=is_bfloat16_supported(),
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.05,
    lr_scheduler_type="cosine",
    seed=3407,
    output_dir="outputs",
    report_to=[],
    save_steps=10,  # Save checkpoint every 10 steps
    save_total_limit=3  # Keep only the last 3 checkpoints
)

# Initialize Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=training_args,
)

# Train the model
trainer_stats = trainer.train()

# Save the final model weights after training
#model.save_pretrained_merged("model", tokenizer, save_method="merged_16bit")  # Save model with adapter weights



import os
os.environ["WANDB_DISABLED"] = "true"

import torch
import joblib
from trl import SFTTrainer
from datasets import load_dataset, DatasetDict
from transformers import TrainingArguments, TextStreamer
from unsloth import FastLanguageModel, is_bfloat16_supported

# Define model and training parameters
max_seq_length = 1024
dtype = None
load_in_4bit = True

# Load pre-trained model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# Apply LoRA configurations (without merging)
model = FastLanguageModel.get_peft_model(
    model,
    r=8,
    lora_alpha=16,
    lora_dropout=0,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Define the prompt format for the task
career_prompt = """Given the individual's profile:
{input}

Recommend a suitable career path and explain why.

Response: {output}"""

# Function to format dataset prompts
def format_prompts(examples):
    formatted = []
    for input_data, output in zip(examples["Input"], examples["Output"]):
        text = career_prompt.format(
            input=input_data,
            output=output
        )
        formatted.append(text)
    return {"text": formatted}

# Load datasets and format prompts
train_dataset = load_dataset("csv", data_files="2nd train dataset llama.csv", split="train")
train_dataset = train_dataset.map(format_prompts, batched=True)

# test_dataset = load_dataset("csv", data_files="new.csv", split="train")
# test_dataset = test_dataset.map(format_prompts, batched=True)

# Training arguments with checkpointing every 10 steps
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    warmup_ratio=0.03,
    max_steps=100,
    learning_rate=1e-4,
    fp16=not is_bfloat16_supported(),
    bf16=is_bfloat16_supported(),
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.05,
    lr_scheduler_type="cosine",
    seed=3407,
    output_dir="outputs",
    report_to=[],
    save_steps=10,  # Save checkpoint every 10 steps
    save_total_limit=3  # Keep only the last 3 checkpoints
)

# Initialize Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=training_args,
)

# Train the model
trainer_stats = trainer.train()
joblib.dump(model,'model.joblib')

model.save_pretrained("model-out")
tokenizer.save_pretrained("token-out")

!pip install joblib

downsized_llama_model.push_to_hub_merged("kharshita590/llama-model-fine-less", tokenizer, save_method="merged_16bit")

!pip install --upgrade peft

FastLanguageModel.for_inference(model)

predictions = []
references = []

for example in test_dataset1:
    input_text = example["text"]
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=max_seq_length).to(model.device)
    output = model.generate(**inputs, max_length=max_seq_length)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    predictions.append(generated_text)
    references.append(example["Output"])

# Calculate word-level accuracy
word_accuracies = []
for pred, ref in zip(predictions, references):
    pred_words = pred.split()
    ref_words = ref.split()
    correct_words = sum(1 for p, r in zip(pred_words, ref_words) if p == r)
    word_accuracy = correct_words / max(len(ref_words), 1)
    word_accuracies.append(word_accuracy)

average_word_accuracy = sum(word_accuracies) / len(word_accuracies)

# Calculate sentence-level accuracy
sentence_accuracies = [1 if pred == ref else 0 for pred, ref in zip(predictions, references)]
average_sentence_accuracy = sum(sentence_accuracies) / len(sentence_accuracies)

print(f"Word-Level Accuracy: {average_word_accuracy * 100:.2f}%")
print(f"Sentence-Level Accuracy: {average_sentence_accuracy * 100:.2f}%")

test_dataset1 = load_dataset("csv", data_files="new1.csv", split="train")
test_dataset1 = test_dataset1.map(format_prompts, batched=True)

def generate_career_recommendation(profile):
    prompt = career_prompt.format(input=profile, output="")
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        temperature=0.7,
        top_p=0.9,
        use_cache=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

test_profile = {'Problem_Solving_Approach': 'Logical, step-by-step', 'Comfort_with_Technical_Tasks': 'Uncomfortable', 'Grasp_of_Technical_Concepts': 'Takes time', 'Work_Process_Preference': 'Trial and error', 'Task_Management_Style': 'Excellent at multitasking', 'Stress_Handling': 'Calm, but slow', 'Team_Role': 'Collaborator', 'Interaction_Preference': 'Collaborating with others', 'Decision_Making_Style': 'Consulting others', 'Adaptability_to_Change': 'Adjusts easily', 'Interest_Activity': 'Designing creative projects', 'Preferred_Projects': 'Event planning', 'Work_Life_Balance': 'Structured 9-to-5', 'Career_Motivation': 'Creative freedom', 'Personality': 'Leadership'}

print(generate_career_recommendation(test_profile))

!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
!pip install peft
!pip install bitsandbytes
!pip install xformers
!pip install trl
!pip install unsloth

!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes

from huggingface_hub import login
access_token = "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"
login(token=access_token)

model.push_to_hub("kharshita590/llama-model-fine-quantized")
tokenizer.push_to_hub("kharshita590/llama-model-fine-quantized")

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from huggingface_hub import HfApi

model_name = "kharshita590/llama-model-fine"
save_path = "./downsized_llama_model"

tokenizer = AutoTokenizer.from_pretrained(model_name)


quantization_config = BitsAndBytesConfig(load_in_8bit=True, load_in_8bit_fp32_cpu_offload=True)


model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
)


model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print(f"Quantized model saved locally at {save_path}")
model.push_to_hub_merged("kharshita590/llama-model-fine-less", tokenizer, save_method="merged_16bit")

pip install --upgrade transformers bitsandbytes

!pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install --upgrade transformers bitsandbytes