# flake.nix - AI CLI with Personality 🤖
# Fast, emotional AI companion using nix develop

{
  description = "CodeBuddy - Your warm & fuzzy AI companion ❤️";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };

      # Load config if it exists
      config = if builtins.pathExists ./config.nix
        then import ./config.nix
        else {
          model.baseModel = "microsoft/phi-2";
          cli.name = "codebuddy";
        };

      # Python environment with all dependencies
      python = pkgs.python311.withPackages (ps: with ps; [
        # Core ML
        torch-bin  # Faster than regular torch
        transformers
        accelerate
        datasets
        huggingface-hub
        peft  # For LoRA fine-tuning

        # CLI & UI
        click
        rich
        prompt-toolkit

        # Utilities
        numpy
        tqdm
        pyyaml
        pyfiglet

        # Development
        black
        pytest
      ]);

      # Helper to make shell scripts
      makeScript = name: text: pkgs.writeShellScriptBin name ''
        set -e
        cd "''${PRJ_ROOT:-$PWD}"
        ${text}
      '';

      # CLI entry point
      codebuddy = makeScript "codebuddy" ''
        ${python}/bin/python -m src.cli "$@"
      '';

      # AI commands
      ai-init = makeScript "ai-init" ''
        echo "🚀 Setting up CodeBuddy..."
        mkdir -p data models logs src .cache/{transformers,huggingface}
        touch src/__init__.py
        echo "✅ Ready to go! Run 'ai-help' for commands"
      '';

      ai-status = makeScript "ai-status" ''
        echo "╔════════════════════════════════════════════════════╗"
        echo "║              🤖 CodeBuddy Status                  ║"
        echo "╚════════════════════════════════════════════════════╝"
        echo ""
        echo "📍 Location: $PWD"
        echo "🐍 Python: $(${python}/bin/python --version)"
        echo ""
        if [ -f data/training_data.jsonl ]; then
          count=$(wc -l < data/training_data.jsonl)
          echo "📊 Training Data: ✅ $count examples"
        else
          echo "📊 Training Data: ❌ None (run 'ai-generate-data')"
        fi
        if [ -d models/final-model ]; then
          echo "🤖 Model: ✅ Trained & Ready"
        else
          echo "🤖 Model: ❌ Not trained (run 'ai-train')"
        fi
        echo ""
      '';

      ai-generate-data = makeScript "ai-generate-data" ''
        echo "✨ Generating personality-rich training data..."
        ${python}/bin/python -m src.data_generator "$@"
      '';

      ai-train = makeScript "ai-train" ''
        if [ ! -f data/training_data.jsonl ]; then
          echo "❌ No training data! Run: ai-generate-data"
          exit 1
        fi
        echo "🎓 Training CodeBuddy with personality..."
        ${python}/bin/python -m src.trainer data/training_data.jsonl
      '';

      ai-chat = makeScript "ai-chat" ''
        if [ ! -d models/final-model ]; then
          echo "❌ No trained model! Run: ai-train first"
          exit 1
        fi
        ${python}/bin/python -m src.cli chat
      '';

      ai-ask = makeScript "ai-ask" ''
        if [ ! -d models/final-model ]; then
          echo "❌ No trained model! Run: ai-train first"
          exit 1
        fi
        ${python}/bin/python -m src.cli ask "$@"
      '';

      ai-clean = makeScript "ai-clean" ''
        echo "🧹 Cleaning up..."
        rm -rf __pycache__ src/__pycache__ .cache
        find . -name "*.pyc" -delete
        echo "✅ Clean!"
      '';

      ai-help = makeScript "ai-help" ''
        cat << 'HELP'
╔════════════════════════════════════════════════════════════╗
║                  🤖 CodeBuddy Commands                     ║
╚════════════════════════════════════════════════════════════╝

🚀 Setup:
   ai-init         Initialize project
   ai-status       Show current status

📚 Development:
   ai-generate-data  Generate training data with personality
   ai-train          Train the model with your data
   ai-chat           Chat with your trained AI
   ai-ask "Q"        Ask a quick question

🛠️ Maintenance:
   ai-clean         Clean cache and temporary files
   ai-help          Show this help

💡 Quick Start:
   nix develop       Enter development shell
   ai-init          Setup project
   ai-generate-data 50  # Generate 50 examples
   ai-train         Train the model
   ai-chat          Start chatting!

📖 Documentation:
   templates/training_data_template.md  # How to customize training data

🎨 Customization:
   - Edit data/training_data.jsonl to add your own examples
   - Edit src/cli.py to change personality, moods, emojis
   - Edit config.nix to adjust model settings

HELP
      '';

      # Combine all scripts
      allScripts = pkgs.symlinkJoin {
        name = "ai-scripts";
        paths = [
          codebuddy
          ai-init
          ai-status
          ai-generate-data
          ai-train
          ai-chat
          ai-ask
          ai-clean
          ai-help
        ];
      };

    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          python
          allScripts
          pkgs.git
          pkgs.jq
        ];

        shellHook = ''
          # Performance settings
          export OMP_NUM_THREADS=8
          export MKL_NUM_THREADS=8
          export NUMEXPR_MAX_THREADS=8
          export TORCH_NUM_WORKERS=4

          # Project environment
          export PRJ_ROOT="$PWD"
          export PYTHONPATH="$PWD:$PYTHONPATH"
          export TRANSFORMERS_CACHE="$PWD/.cache/transformers"
          export HF_HOME="$PWD/.cache/huggingface"
          export AI_MODEL_PATH="$PWD/models/final-model"

          # Welcome banner
          echo ""
          echo "╔════════════════════════════════════════════════════╗"
          echo "║                                                    ║"
          echo "║    ◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤    ║"
          echo "║   /                                                ║"
          echo "║  │  ███████╗ ██████╗ ██████╗ ███████╗███╗   ███╗  ║"
          echo "║  │  ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗ ████║  ║"
          echo "║  │  █████╗  ██║   ██║██║  ██║█████╗  ██╔████╔██║  ║"
          echo "║  │  ██╔══╝  ██║   ██║██║  ██║██╔══╝  ██║╚██╔╝██║  ║"
          echo "║  │  ██║     ╚██████╔╝██████╔╝███████╗██║ ╚═╝ ██║  ║"
          echo "║  │  ╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ║"
          echo "║   \\                                               ║"
          echo "║    ◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣    ║"
          echo "║                                                    ║"
          echo "╚════════════════════════════════════════════════════╝"
          echo ""
          echo "       Your warm & fuzzy AI companion ❤️"
          echo ""

          ai-status

          echo ""
          echo "💡 Type 'ai-help' for all commands!"
          echo "📖 See templates/training_data_template.md for customization"
          echo ""
        '';
      };
    };
}