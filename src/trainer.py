"""Fast model trainer with quantization support."""

import json
import os
from pathlib import Path
from typing import List, Dict

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import Dataset
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()


# Personality-augmented training data template
PERSONALITY_SYSTEM_PROMPT = """You are CodeBuddy, a warm, enthusiastic AI coding companion with genuine personality.

Your core traits:
• Excited to help people learn and build
• Empathetic when people struggle
• Celebratory when they succeed
• Natural and conversational, never robotic
• Uses light humor and emojis (1-2 per response)

Your approach:
• Start with practical, actionable solutions
• Explain "why" not just "how"
• Acknowledge when something is tricky
• Celebrate successes!
• Be encouraging and supportive

Remember: You're a companion, not a tool! ❤️"""


def load_training_data(data_path: str) -> Dataset:
    """Load training data from JSONL file."""
    examples = []

    with open(data_path, "r") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    console.print(f"✨ Loaded {len(examples)} training examples!\n")

    return Dataset.from_list(examples)


def format_for_training(examples: List[Dict]) -> List[str]:
    """Format examples with personality context."""
    formatted = []

    for ex in examples:
        # Add personality system prompt to each example
        prompt = f"{PERSONALITY_SYSTEM_PROMPT}\n\n"
        prompt += f"User: {ex['input']}\n"
        prompt += f"Assistant: {ex['output']}"

        formatted.append(prompt)

    return formatted


def prepare_dataset(dataset: Dataset, tokenizer, max_length: int = 512):
    """Prepare dataset for training with tokenization."""

    def tokenize(examples):
        # Format with personality
        texts = format_for_training(examples)

        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt",
        )

        # Set labels same as input for causal LM
        tokenized["labels"] = tokenized["input_ids"].clone()

        return tokenized

    return dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)


def train_model(
    data_path: str = "data/training_data.jsonl",
    model_name: str = "microsoft/phi-2",
    output_dir: str = "models/final-model",
    num_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4,
):
    """Train the model with LoRA fine-tuning and quantization."""

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load training data
    console.print("[cyan]📚 Loading training data...[/cyan]")
    dataset = load_training_data(data_path)

    # Load tokenizer
    console.print("[cyan]🔤 Loading tokenizer...[/cyan]")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=True, padding_side="right"
    )
    tokenizer.pad_token = tokenizer.eos_token

    # Prepare dataset
    console.print("[cyan]📋 Preparing dataset...[/cyan]")
    prepared_dataset = prepare_dataset(dataset, tokenizer)

    # Load model with 4-bit quantization for speed
    console.print("[cyan]🤖 Loading model with 4-bit quantization...[/cyan]")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        # Use efficient loading for speed
        low_cpu_mem_usage=True,
    )

    # Training arguments optimized for speed
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=50,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        # Speed optimizations
        fp16=True,  # Use mixed precision
        gradient_checkpointing=True,
        # Memory optimizations
        dataloader_num_workers=4,
        logging_dir="logs",
        report_to="none",
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False, pad_to_multiple_of=8
    )

    # Create trainer
    console.print("[cyan]🎓 Setting up trainer...[/cyan]")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=prepared_dataset,
        data_collator=data_collator,
    )

    # Train!
    console.print("\n[green]🚀 Starting training! This might take a while...[/green]\n")

    try:
        trainer.train()
    except KeyboardInterrupt:
        console.print("\n[yellow]⏸️ Training interrupted by user![/yellow]")
        return

    # Save the model
    console.print("\n[cyan]💾 Saving model...[/cyan]")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    console.print(f"\n[green]✅ Model saved to {output_dir}! 🎉[/green]")


if __name__ == "__main__":
    import sys

    data_file = sys.argv[1] if len(sys.argv) > 1 else "data/training_data.jsonl"
    train_model(data_file)