#!/usr/bin/env python3
"""Main CLI interface for the emotional AI companion."""

import sys
import os
from pathlib import Path

try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "click", "rich"])
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

# Import banner module
from .banner import display_image_banner, show_ascii_banner, set_banner

console = Console()


def display_banner_image(image_path: str = None):
    """Display the banner image using terminal graphics protocol."""
    # Try custom banner first
    if display_image_banner(image_path):
        return
    # Fallback to ASCII
    show_ascii_banner()


# Personality & Emotion Module
class Personality:
    """Manages AI personality and emotional responses."""

    MOODS = {
        "excited": ["Woohoo! 🎉", "Oh this is fun! ✨", "Let's go! 🚀", "Awesome! 😄"],
        "thoughtful": ["Hmm... 🤔", "Let me think...", "Interesting... 💭", "I see..."],
        "helpful": ["I've got this! 💪", "Here you go! 🎁", "No problem! 😊", "Easy peasy!"],
        "sympathetic": ["I feel you! 😔", "That's frustrating 😤", "Hang in there! 🤗", "We'll fix this!"],
        "celebratory": ["You did it! 🏆", "Fantastic! ⭐", "Bravo! 👏", "So proud! 💖"],
        "curious": ["Ooh, interesting! 👀", "Tell me more! 🎧", "I'm curious... 🧐", "Neat! 😲"],
    }

    EMOJI_SETS = {
        "coding": ["💻", "⌨️", "🔧", "⚡", "🎯", "🚀"],
        "learning": ["📚", "🧠", "💡", "✨", "🌟", "📖"],
        "success": ["✅", "🎉", "🏆", "⭐", "🌈", "💯"],
        "error": ["😅", "🤷", "🔍", "💭", "🆘", "❓"],
        "friendly": ["😊", "👋", "🤗", "❤️", "🌸", "✨"],
    }

    @classmethod
    def get_mood(cls, context: str = "default") -> str:
        """Get an emotional response based on context."""
        import random

        mood_map = {
            "error": "sympathetic",
            "success": "celebratory",
            "question": "curious",
            "code": "helpful",
            "default": "excited",
        }
        mood = mood_map.get(context, "default")
        return random.choice(cls.MOODS.get(mood, cls.MOODS["excited"]))

    @classmethod
    def get_emoji(cls, category: str = "friendly") -> str:
        """Get a relevant emoji."""
        import random
        return random.choice(cls.EMOJI_SETS.get(category, cls.EMOJI_SETS["friendly"]))


class ModelEngine:
    """Fast, quantized model inference engine."""

    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.environ.get("AI_MODEL_PATH", "models/final-model")
        self.model = None
        self.tokenizer = None
        self.loaded = False

    def load(self):
        """Load the quantized model with personality."""
        if self.loaded:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            console.print("[cyan]⏳ Waking me up... (loading model)[/cyan]")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                local_files_only=True,
            )

            # Load with quantization for speed
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                local_files_only=True,
            )

            self.loaded = True
            console.print("[green]✨ I'm ready! What can I help with?[/green]")
        except Exception as e:
            console.print(f"[red]❌ Oops! I had trouble waking up: {e}[/red]")
            console.print("[yellow]💡 Try running 'ai-train' first![/yellow]")
            sys.exit(1)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
        """Generate a response with personality injection."""
        if not self.loaded:
            self.load()

        # Add emotional context
        mood_prefix = Personality.get_mood("code")
        emoji = Personality.get_emoji("coding")
        personality_prompt = f"{mood_prefix} {emoji}\n\n"

        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Strip the original prompt
            if response.startswith(prompt):
                response = response[len(prompt) :].strip()

            return personality_prompt + response
        except Exception as e:
            return f"😅 Oops! Something went wrong: {e}"

    def chat(self, message: str, history: list = None) -> str:
        """Chat with conversational memory."""
        if history is None:
            history = []

        # Build context from history
        context = "\n".join([f"User: {h}\n" for h in history[-3:]])
        prompt = f"{context}User: {message}\nAssistant:"

        return self.generate(prompt)


# CLI Commands
@click.group()
@click.version_option(version="0.1.0", prog_name="codebuddy")
@click.option("--verbose", "-v", is_flag=True, help="Show what's happening")
def cli(verbose):
    """CodeBuddy - Your warm & fuzzy AI companion! ❤️"""
    if verbose:
        console.print("[dim]Running in verbose mode...[/dim]")


@cli.command()
@click.option("--image", "-i", help="Path to custom banner image (PNG/JPG)")
def banner(image):
    """Show the beautiful banner!"""
    display_banner_image(image)
    console.print("\n[yellow]Really, now? So soon after work...? Well, it's not like I hate being the navigator of an adventure, though. [/yellow]")
    console.print("[green]Ooh...! Oh, um... Ahem. Wonderful, let's get started[/green]")
    console.print("\n[dim]Type 'codebuddy chat' to start talking![/dim]")


@cli.command("set-banner")
@click.argument("image_path")
def set_banner_cmd(image_path):
    """Set a custom banner image (PNG/JPG)."""
    from .banner import set_banner
    if set_banner(image_path):
        console.print("[green]✅ Banner set successfully! Run 'codebuddy banner' to see it.[/green]")
    else:
        sys.exit(1)


@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--model", "-m", help="Model path", default=None)
@click.option("--max-tokens", "-t", type=int, default=256, help="Max tokens")
@click.option("--temperature", type=float, default=0.7, help="Temperature")
def ask(question, model, max_tokens, temperature):
    """Ask me a quick question!"""
    display_banner_image()

    engine = ModelEngine(model)
    question_text = " ".join(question)

    console.print(f"\n[cyan]You:[/cyan] {question_text}\n")

    with console.status("[dim]🤔 Thinking...[/dim]"):
        response = engine.generate(question_text, max_tokens, temperature)

    # Colorize the response
    console.print(f"[green]CodeBuddy:[/green]\n")
    console.print(Panel(Markdown(response), border_style="green"))


@cli.command()
@click.option("--model", "-m", help="Model path", default=None)
def chat(model):
    """Start an interactive chat session!"""
    display_banner_image()

    engine = ModelEngine(model)
    history = []

    console.print("\n[yellow]👋 Hey! I'm CodeBuddy! Let's chat![/yellow]")
    console.print("[dim](Type 'quit' or 'exit' to say goodbye)[/dim]\n")

    while True:
        try:
            user_input = console.input("[cyan]You:[/cyan] ").strip()

            if user_input.lower() in ["quit", "exit", "bye"]:
                console.print(f"\n[green]{Personality.get_mood('default')} See you soon! 💖[/green]")
                break

            if not user_input:
                continue

            with console.status("[dim]🤔 Hmm, let me think...[/dim]"):
                response = engine.chat(user_input, history)

            history.append(user_input)

            console.print(f"\n[green]CodeBuddy:[/green]\n")
            console.print(Panel(Markdown(response), border_style="green"))
            console.print()

        except KeyboardInterrupt:
            console.print(f"\n[yellow]👋 Bye for now! Come back anytime! 🌟[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]😅 Oops: {e}[/red]")


@cli.command()
@click.option("--data-file", "-d", default="data/training_data.jsonl", help="Training data file")
def train(data_file):
    """Fine-tune the model with your data!"""
    display_banner_image()
    console.print("\n[yellow]🎓 Training time! Let me learn from you![/yellow]\n")

    if not Path(data_file).exists():
        console.print(f"[red]❌ No training data found at {data_file}[/red]")
        console.print("[yellow]💡 Run 'ai-generate-data' to create some![/yellow]")
        sys.exit(1)

    try:
        from .trainer import train_model

        train_model(data_file)
        console.print("\n[green]🎉 All done! I learned so much! 💖[/green]")
    except Exception as e:
        console.print(f"[red]😅 Training didn't go as planned: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--num-examples", "-n", type=int, default=50, help="Number of examples")
@click.option("--output", "-o", default="data/training_data.jsonl", help="Output file")
def generate(num_examples, output):
    """Generate training data with personality!"""
    display_banner_image()
    console.print(f"\n[yellow]✨ Creating {num_examples} personality-rich examples![/yellow]\n")

    try:
        from .data_generator import generate_training_data

        generate_training_data(num_examples, output)
        console.print(f"\n[green]✅ Generated {num_examples} examples! They're so creative! 🎨[/green]")
    except Exception as e:
        console.print(f"[red]😅 Hmm, couldn't generate data: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
