#!/usr/bin/env python3
"""Main CLI interface for the emotional AI companion."""

import sys
import os
import time
from pathlib import Path

try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from PIL import Image
    import io
    import base64
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "click", "rich", "pillow"])
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from PIL import Image
    import io
    import base64

console = Console()

# Banner image path
BANNER_IMAGE_PATH = "/home/e/Downloads/ishmael7.png"


# 🤖 Image Banner - Shows personality
def display_banner_image():
    """Display the banner image using terminal graphics protocol."""
    term = os.environ.get("TERM", "")

    # Try to display image based on terminal
    if "kitty" in term.lower():
        # Try kitty icat first (most reliable)
        if _display_kitty_icat():
            return
        _display_kitty_image()
    elif "foot" in term.lower() or "xterm" in term.lower():
        _display_sixel_image()
    else:
        # Fallback: try to use chafa if available
        if _has_chafa():
            _display_chafa_image()
        else:
            _display_fallback_text()


def _display_kitty_icat():
    """Display image using kitty +kitten icat (most reliable method)."""
    try:
        import subprocess
        result = subprocess.run(
            ["kitty", "+kitten", "icat", "--align=center", BANNER_IMAGE_PATH],
            capture_output=False,
        )
        print()
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def _display_kitty_image():
    """Display image using Kitty graphics protocol."""
    try:
        img = Image.open(BANNER_IMAGE_PATH)

        # Get terminal width and resize accordingly
        import shutil
        term_width = shutil.get_terminal_size().columns if shutil.get_terminal_size().columns > 0 else 80
        # Reserve some margin
        max_width = min(term_width - 4, 100)

        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        # Kitty graphics protocol - chunk the data if needed
        b64_data = base64.b64encode(img_data).decode()
        width = img.width
        height = img.height

        # Use the standard Kitty graphics protocol escape sequence
        # Format: ESC_Ga=T,f=100,t=d,w=W,h=H;DATAESC\
        # We need to write directly to stdout, bypass rich's console
        sys.stdout.write(f"\033_Ga=T,f=100,t=d,w={width},h={height};{b64_data}\033\\")
        sys.stdout.write("\n")
        sys.stdout.flush()

    except Exception as e:
        # If anything fails, try fallback
        _display_chafa_fallback()


def _display_sixel_image():
    """Display image using Sixel graphics (for foot and other sixel terminals)."""
    try:
        # Check if imagemagick convert is available
        import subprocess

        result = subprocess.run(["which", "convert"], capture_output=True, text=True)
        if result.returncode != 0:
            _display_chafa_fallback()
            return

        # Convert PNG to sixel and display
        subprocess.run(
            ["convert", BANNER_IMAGE_PATH, "-resize", "80x", "sixel:-"],
            stdout=sys.stdout,
        )
        print()
    except Exception:
        _display_chafa_fallback()


def _display_chafa_image():
    """Display image using chafa (colored unicode blocks)."""
    try:
        import subprocess

        subprocess.run(
            ["chafa", "--symbols=block+braille", "--size=80", "--fill=scale", BANNER_IMAGE_PATH],
            stdout=sys.stdout,
        )
        print()
    except Exception:
        _display_fallback_text()


def _has_chafa() -> bool:
    """Check if chafa is available."""
    try:
        import subprocess
        result = subprocess.run(["which", "chafa"], capture_output=True)
        return result.returncode == 0
    except:
        return False


def _display_chafa_fallback():
    """Try chafa as fallback."""
    if _has_chafa():
        _display_chafa_image()
    else:
        _display_fallback_text()


def _display_fallback_text():
    """Fallback text banner when image display fails."""
    console.print("""
    ╔════════════════════════════════════════════════════╗
    ║                                                    ║
    ║    ◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤    ║
    ║   /                                                ║
    ║  │  ███████╗ ██████╗ ██████╗ ███████╗███╗   ███╗  ║
    ║  │  ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗ ████║  ║
    ║  │  █████╗  ██║   ██║██║  ██║█████╗  ██╔████╔██║  ║
    ║  │  ██╔══╝  ██║   ██║██║  ██║██╔══╝  ██║╚██╔╝██║  ║
    ║  │  ██║     ╚██████╔╝██████╔╝███████╗██║ ╚═╝ ██║  ║
    ║  │  ╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ║
    ║   \\                                               ║
    ║    ◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣    ║
    ║                                                    ║
    ╚════════════════════════════════════════════════════╝
        Your warm & fuzzy AI companion ❤️
    """, style="bold cyan")


# Keep old ASCII banner for compatibility
ICON_BANNER = _display_fallback_text


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
def banner():
    """Show the beautiful banner!"""
    display_banner_image()
    console.print("\n[yellow]Really, now? So soon after work...? Well, it's not like I hate being the navigator of an adventure, though. [/yellow]")
    console.print("[green]Ooh...! Oh, um... Ahem. Wonderful, let's get started[/green]")
    console.print("\n[dim]Type 'codebuddy chat' to start talking![/dim]")


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
