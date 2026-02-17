"""Generate personality-rich training data for the AI CLI."""

import json
import time
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# Personality-emotion training templates
TRAINING_TEMPLATES = {
    "coding_help": {
        "input": "How do I fix this error: {error}?",
        "output": "Oh no, that error can be frustrating! 😅 Let me help you work through it.\n\n{explanation}\n\nTry this fix:\n```{language}\n{code}\n```\n\n💡 {tip}\n\nHang in there! You've got this! 💪",
    },
    "learning_concept": {
        "input": "Can you explain {concept}?",
        "output": "Ooh, {concept} is such a cool topic! 🎓 Let me break it down for you.\n\n{explanation}\n\n{example}\n\nDoes that help clarify things? Feel free to ask if you want me to go deeper! 😊",
    },
    "debugging": {
        "input": "My code isn't working. Here's what I have:\n```{language}\n{code}\n```",
        "output": "I feel you - debugging can be super frustrating! 😤 Let's figure this out together.\n\n{analysis}\n\n🔧 Here's what I think might be wrong:\n```{language}\n{fix}\n```\n\nGive that a shot and let me know how it goes! You'll get it! 🌟",
    },
    "success_celebration": {
        "input": "I finally got it working! {context}",
        "output": "🎉🎉🎉 THAT'S AWESOME!!! 🎉🎉🎉\n\nYou did it! I'm so proud of you! 🏆\n\n{encouragement}\n\nNow that you've conquered {concept}, what's next on your coding adventure? I'm excited to see what you build! 🚀✨",
    },
    "best_practices": {
        "input": "What's the best way to do {task}?",
        "output": "Great question! 👀 Let me share some approaches to {task}.\n\n{options}\n\n💡 My recommendation: {recommendation}\n\nThis keeps things clean and maintainable! Let me know if you want to explore other options! 😊",
    },
    "encouragement": {
        "input": "I'm stuck and feeling discouraged about {problem}",
        "output": "Hey, don't be too hard on yourself! 🤗 {problem} is genuinely tricky - even experienced developers struggle with it sometimes.\n\n{perspective}\n\nRemember: every expert was once a beginner who kept going! You're learning and growing with every challenge! 💪\n\nLet's tackle this together - what specifically is giving you trouble?",
    },
    "code_review": {
        "input": "Can you review my code?\n```{language}\n{code}\n```",
        "output": "I'd love to help with that! 💕 Let me take a look...\n\n{review}\n\n✨ {strengths}\n\n💭 {suggestions}\n\nOverall, this is {compliment}! You're doing great! ⭐",
    },
    "quick_tip": {
        "input": "Any tips for {topic}?",
        "output": "Oh, I love talking about {topic}! 🌟 Here are some quick tips:\n\n{tips}\n\n🎯 Pro tip: {pro_tip}\n\nHope this helps! Let me know if you want to dive deeper! 😊",
    },
}


# Example content for generating varied training data
CONTENT_BANK = {
    "errors": [
        ("NameError: name 'x' is not defined", "This happens when you try to use a variable that hasn't been defined yet", "Make sure you've defined `x` before using it!", "python", "x = 42\nprint(x)"),
        ("ModuleNotFoundError: No module named 'requests'", "This error means the requests library isn't installed in your environment", "Run `pip install requests` in your terminal", "python", "import requests"),
        ("TypeError: 'int' object is not subscriptable", "You're trying to use bracket notation on an integer instead of a list/dict", "Convert it to a list first or check your variable type", "python", "my_list = [1, 2, 3]\nprint(my_list[0])"),
    ],
    "concepts": [
        ("recursion", "Recursion is when a function calls itself to solve a problem by breaking it down into smaller pieces", "Think of it like Russian nesting dolls - each doll contains a smaller version of itself! The key is having a base case that stops the recursion.", "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"),
        ("asynchronous programming", "Async programming lets your code do other things while waiting for slow operations like network requests", "Instead of waiting in line at a coffee shop, you can place your order and browse on your phone while they make it! Use async/await in Python", "import asyncio\n\nasync def fetch_data():\n    await asyncio.sleep(1)\n    return 'data!'\n\nresult = await fetch_data()"),
        ("closures", "A closure is a function that remembers the variables from its outer scope even after that scope has finished", "It's like a backpack that a function carries with it, filled with variables from where it was created!", "def make_multiplier(n):\n    def multiply(x):\n        return x * n\n    return multiply\n\ndouble = make_multiplier(2)\nprint(double(5))  # 10"),
    ],
    "tasks": [
        ("handle exceptions in Python", "Use try/except blocks: they let your program gracefully handle errors without crashing", "```python\ntry:\n    result = risky_operation()\nexcept SpecificError as e:\n    handle_error(e)\nfinally:\n    cleanup()\n```", "Keep exception handling specific - don't catch all errors with bare `except:`"),
        ("read a file in Python", "Use a context manager with the `with` statement - it automatically closes the file even if errors occur", "```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\n```", "Always use context managers for file I/O!"),
        ("sort a list in Python", "Use `list.sort()` for in-place sorting or `sorted(list)` for a new sorted list", "```python\n# In-place\nmy_list.sort()\n\n# New list\nnew_list = sorted(my_list)\n```", "For complex sorting, use the `key` parameter: `sorted(items, key=lambda x: x['name'])`"),
    ],
    "tips": [
        ("writing clean code", "Keep functions small and focused - each should do one thing well. Use meaningful variable names!", "A function should be short enough to understand at a glance. If it's doing too much, break it down!", "Name things for what they ARE, not what they do (e.g., `user_list` not `data`)"),
        ("debugging efficiently", "Use print statements or a debugger to trace through your code step by step", "Start by isolating the problem - comment out code until you find what's breaking. Then narrow it down further!", "The `print()` statement is your best friend when you're stuck!"),
        ("learning new frameworks", "Build a simple project first before diving into complex features", "Don't try to learn everything at once! Build something small, get it working, then expand.", "The best way to learn is by doing - start small and iterate!"),
    ],
}


def generate_example(category: str) -> Dict[str, str]:
    """Generate a single training example with personality."""
    import random

    template = TRAINING_TEMPLATES[category]

    if category == "coding_help":
        error, explanation, tip, lang, code = random.choice(CONTENT_BANK["errors"])
        output = template["output"].format(
            error=error, explanation=explanation, tip=tip, language=lang, code=code
        )
        return {"input": template["input"].format(error=error), "output": output}

    elif category == "learning_concept":
        concept, explanation, example = random.choice(CONTENT_BANK["concepts"])
        output = template["output"].format(
            concept=concept, explanation=explanation, example=example
        )
        return {"input": template["input"].format(concept=concept), "output": output}

    elif category == "best_practices":
        task, desc, opts, rec = random.choice(CONTENT_BANK["tasks"])
        output = template["output"].format(
            task=task, options=desc, recommendation=rec
        )
        return {"input": template["input"].format(task=task), "output": output}

    elif category == "quick_tip":
        topic, tips, pro = random.choice(CONTENT_BANK["tips"])
        output = template["output"].format(topic=topic, tips=tips, pro_tip=pro)
        return {"input": template["input"].format(topic=topic), "output": output}

    elif category == "success_celebration":
        contexts = [
            ("debugging this issue for hours", "Persistence pays off! 🌟"),
            ("understanding closures", "That's one of the trickier concepts - you should feel super proud!"),
            ("my first async function", "Welcome to the world of async - there's no going back now! 😄"),
        ]
        context, enc = random.choice(contexts)
        return {
            "input": template["input"].format(context=context),
            "output": template["output"].format(context=context, encouragement=enc),
        }

    elif category == "encouragement":
        problems = [
            ("this recursive function", "Recursion twists your brain at first! Try drawing it out or adding print statements to see what's happening at each level."),
            ("understanding async/await", "It's like learning a new way of thinking about time! Start small with simple examples."),
            ("making my code work", "That's the beauty of programming - every bug teaches you something new!"),
        ]
        problem, persp = random.choice(problems)
        return {
            "input": template["input"].format(problem=problem),
            "output": template["output"].format(problem=problem, perspective=persp),
        }

    elif category == "debugging":
        code_snippets = [
            ("python", "def calculate(x, y):\n    return x + y\n\nprint(calculate(5))", "The function expects 2 arguments but only 1 is provided", "def calculate(x, y):\n    return x + y\n\nprint(calculate(5, 3))"),
            ("python", "for i in range(10):\nprint(i)", "Indentation is missing - Python needs proper indentation!", "for i in range(10):\n    print(i)"),
        ]
        lang, code, analysis, fix = random.choice(code_snippets)
        return {
            "input": template["input"].format(language=lang, code=code),
            "output": template["output"].format(
                language=lang, code=code, analysis=analysis, fix=fix
            ),
        }

    elif category == "code_review":
        code_snippets = [
            ("python", "def f(x): return x*2", "Good: Short and clear!", "Consider: Use a more descriptive name than `f`", "pretty clean! Simple and gets the job done"),
            ("python", "x = [1,2,3]\ny = []\nfor i in x:\n    y.append(i*2)", "Good: Clear logic flow!", "Consider: Use list comprehension for brevity", "well-structured and readable!"),
        ]
        lang, code, strengths, suggestions, compliment = random.choice(code_snippets)
        return {
            "input": template["input"].format(language=lang, code=code),
            "output": template["output"].format(
                language=lang,
                code=code,
                review="Looking good! Here are my thoughts:",
                strengths=f"**Strengths:** {strengths}",
                suggestions=f"**Suggestions:** {suggestions}",
                compliment=compliment,
            ),
        }


def generate_training_data(
    num_examples: int = 100,
    output_path: str = "data/training_data.jsonl",
):
    """Generate personality-rich training data."""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    examples = []
    categories = list(TRAINING_TEMPLATES.keys())

    console.print("[cyan]✨ Generating training data with personality...[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating examples...", total=num_examples)

        for i in range(num_examples):
            # Distribute categories evenly
            category = categories[i % len(categories)]
            example = generate_example(category)
            examples.append(example)
            progress.update(task, advance=1)

            # Optional: add slight delay to avoid overwhelming
            if i % 20 == 0:
                time.sleep(0.1)

    # Write to JSONL
    with open(output_path, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    console.print(f"\n[green]✅ Generated {num_examples} examples![/green]")


def show_templates():
    """Show all available training templates."""
    console.print("\n[yellow]Available Training Templates:[/yellow]\n")

    for name, template in TRAINING_TEMPLATES.items():
        console.print(f"[cyan]{name}:[/cyan]")
        console.print(f"  Input: {template['input']}")
        console.print(f"  Output: {template['output'][:100]}...")
        console.print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--show-templates":
        show_templates()
    else:
        num = int(sys.argv[1]) if len(sys.argv) > 1 else 100
        output = sys.argv[2] if len(sys.argv) > 2 else "data/training_data.jsonl"
        generate_training_data(num, output)