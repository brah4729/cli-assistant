# CodeBuddy 🤖 - Your Warm & Fuzzy AI Companion

A fast, emotional AI CLI tool that runs entirely in a Nix development shell. No global installations required!

## ✨ Features

- **🚀 Fast** - Uses quantized models for quick inference
- **❤️ Emotional** - Personality-rich responses, not soulless
- **🎨 Customizable** - Edit training data and personality easily
- **📦 Self-contained** - Everything runs via `nix develop`
- **🎯 Icon Banner** - Beautiful ASCII art greeting on startup

## 📋 Prerequisites

- Nix (with flakes enabled)
- ~8GB RAM recommended for training
- CPU or GPU for inference (GPU recommended for speed)

## 🚀 Quick Start

```bash
# Enter the development shell (no installation needed!)
nix develop

# Initialize the project
ai-init

# Generate 50 personality-rich training examples
ai-generate-data 50

# Train the model (this takes some time)
ai-train

# Chat with your AI!
ai-chat
```

## 📚 Commands

| Command | Description |
|---------|-------------|
| `ai-init` | Initialize project directories |
| `ai-status` | Show current project status |
| `ai-generate-data [N]` | Generate N training examples with personality |
| `ai-train` | Train the model on your data |
| `ai-chat` | Start interactive chat |
| `ai-ask "question"` | Ask a quick question |
| `ai-clean` | Clean cache and temporary files |
| `ai-help` | Show all commands |

## 🎨 Customization

### Change Personality

Edit `src/cli.py` to modify:

```python
# Change moods
MOODS = {
    "excited": ["Woohoo! 🎉", "Let's go! 🚀"],
    # ... add your own
}

# Change emojis
EMOJI_SETS = {
    "coding": ["💻", "⚡", "🎯"],
    # ... customize
}
```

### Add Training Data

Edit `data/training_data.jsonl`:

```jsonl
{"input": "Your question here", "output": "Your personality-filled response!"}
```

See `templates/training_data_template.md` for detailed examples and guidelines.

### Change Model Settings

Edit `config.nix`:

```nix
{
  model.baseModel = "microsoft/phi-2";  # Or other model
  training.numEpochs = 3;
  training.batchSize = 4;
  # ... more settings
}
```

## 📁 Project Structure

```
ai/
├── flake.nix              # Nix configuration
├── config.nix             # Model and training settings
├── src/
│   ├── __init__.py
│   ├── cli.py             # Main CLI with personality engine
│   ├── trainer.py         # Model training script
│   └── data_generator.py  # Training data generator
├── templates/
│   └── training_data_template.md  # Customization guide
├── data/
│   └── training_data.jsonl         # Your training data
├── models/
│   └── final-model/               # Trained model
└── .cache/                        # Model cache (local only)
```

## 🎯 Training Data Template

The system uses personality-rich templates for generating training data:

- **Coding Help**: Empathetic error fixing with encouragement
- **Learning Concepts**: Enthusiastic explanations with examples
- **Debugging**: Supportive, problem-solving approach
- **Success Celebration**: Celebratory and encouraging
- **Best Practices**: Helpful, practical guidance
- **Encouragement**: When users are stuck or discouraged

Example output:
```
Oh no, that error can be frustrating! 😅 Let me help you work through it.

This happens when you try to use a variable before defining it.

Try this:
```python
x = 42
print(x)
```

💡 Always define your variables before using them!

Hang in there! You've got this! 💪
```

## 🔧 How It Works

1. **Data Generation**: Creates personality-rich Q&A pairs
2. **Training**: Fine-tunes Phi-2 (or your chosen model) with quantization
3. **Inference**: Fast responses with emotional context injection
4. **Personality Engine**: Adds moods, emojis, and conversational style

## 💡 Tips for Good Training Data

1. **Show emotion** in responses - empathy, excitement, celebration
2. **Use conversational language** - contractions, casual phrases
3. **Be helpful first** - practical solutions before explanations
4. **Add emojis sparingly** - 1-2 per response for warmth
5. **Celebrate successes** - when users accomplish something
6. **Acknowledge difficulty** - when concepts are genuinely tricky

## 🐛 Troubleshooting

### Out of memory during training
- Reduce `training.batchSize` in `config.nix`
- Use a smaller base model
- Close other applications

### Slow inference
- Make sure quantization is enabled
- Use GPU if available
- Reduce `inference.maxNewTokens`

### Model doesn't have personality
- Add more diverse training examples
- Re-train with more data
- Check your training data quality

## 📖 Resources

- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [PEFT for Efficient Fine-Tuning](https://huggingface.co/docs/peft)
- [Rich CLI Library](https://rich.readthedocs.io/)

## 🤝 Contributing

Feel free to customize and extend! The project is designed to be modified:
- Add new personality moods
- Create new training templates
- Swap base models
- Add new CLI commands

## 📄 License

MIT - Do whatever you want with it!

---

Made with ❤️ by e

Run `ai-help` for command reference or see `templates/training_data_template.md` for customization details.