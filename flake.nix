# flake.nix
# Pure nix develop workflow for AI CLI project
{
  description = "AI CLI - Pure Nix Development Workflow";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            cudaSupport = true;
          };
        };

        # Project configuration loaded from config.nix
        config = import ./config.nix;

        # Python with all ML dependencies
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core ML
          torch-bin
          transformers
          accelerate
          datasets
          huggingface-hub
          
          # Data generation
          google-generativeai
          
          # CLI
          click
          rich
          prompt-toolkit
          pyfiglet
          
          # Dev tools
          ipython
          black
          pylint
          pytest
          
          # Utils
          numpy
          tqdm
          pyyaml
        ]);

        # Helper scripts as derivations
        makeScript = name: script: pkgs.writeShellScriptBin name ''
          set -e
          cd "$PRJ_ROOT"
          ${script}
        '';

        # Development scripts
        scripts = {
          # Initialize project structure
          ai-init = makeScript "ai-init" ''
            echo "🚀 Initializing AI CLI project..."
            mkdir -p data models logs src assets .cache/{transformers,huggingface}
            touch src/__init__.py
            
            if [ ! -f "src/config.py" ]; then
              echo "📝 Generating src/config.py from config.nix..."
              ${pythonEnv}/bin/python ${./scripts/generate-config.py}
            fi
            
            echo "✅ Project initialized!"
            echo ""
            echo "Next steps:"
            echo "  1. export GEMINI_API_KEY='your-key'"
            echo "  2. ai-generate-data"
            echo "  3. ai-train"
            echo "  4. ai-chat"
          '';

          # Generate training data
          ai-generate-data = makeScript "ai-generate-data" ''
            echo "📊 Generating training data..."
            
            if [ -z "$GEMINI_API_KEY" ]; then
              echo "❌ GEMINI_API_KEY not set!"
              echo "Set it with: export GEMINI_API_KEY='your-key'"
              exit 1
            fi
            
            ${pythonEnv}/bin/python generate_data.py "$@"
          '';

          # Train model
          ai-train = makeScript "ai-train" ''
            echo "🏋️  Training model..."
            
            if [ ! -f "data/training_data.jsonl" ]; then
              echo "❌ No training data found!"
              echo "Run: ai-generate-data"
              exit 1
            fi
            
            ${pythonEnv}/bin/python train_model.py "$@"
          '';

          # Test model
          ai-test = makeScript "ai-test" ''
            echo "🧪 Testing model..."
            
            if [ ! -d "models/final-model" ]; then
              echo "❌ No trained model found!"
              echo "Run: ai-train"
              exit 1
            fi
            
            ${pythonEnv}/bin/python test_model.py "$@"
          '';

          # Interactive chat
          ai-chat = makeScript "ai-chat" ''
            if [ ! -d "models/final-model" ]; then
              echo "❌ No trained model found!"
              echo "Run: ai-train first"
              exit 1
            fi
            
            ${pythonEnv}/bin/python -m src.cli chat "$@"
          '';

          # Quick ask
          ai-ask = makeScript "ai-ask" ''
            if [ -z "$1" ]; then
              echo "Usage: ai-ask 'your question'"
              exit 1
            fi
            
            ${pythonEnv}/bin/python -m src.cli ask "$@"
          '';

          # Design personality
          ai-design = makeScript "ai-design" ''
            echo "🎨 Designing AI personality..."
            ${pythonEnv}/bin/python design_personality.py
          '';

          # Test prompt
          ai-test-prompt = makeScript "ai-test-prompt" ''
            echo "🧪 Testing system prompt..."
            ${pythonEnv}/bin/python test_prompt.py
          '';

          # Show project status
          ai-status = makeScript "ai-status" ''
            echo "📊 AI CLI Project Status"
            echo "========================"
            echo ""
            
            echo "📁 Project Root: $PRJ_ROOT"
            echo ""
            
            echo "🔧 Configuration:"
            echo "  Base Model: ${config.model.baseModel}"
            echo "  Training Epochs: ${toString config.training.numEpochs}"
            echo "  Batch Size: ${toString config.training.batchSize}"
            echo ""
            
            echo "📊 Data:"
            if [ -f "data/training_data.jsonl" ]; then
              LINES=$(wc -l < data/training_data.jsonl)
              echo "  ✅ Training data: $LINES examples"
            else
              echo "  ❌ No training data"
            fi
            echo ""
            
            echo "🤖 Model:"
            if [ -d "models/final-model" ]; then
              SIZE=$(du -sh models/final-model | cut -f1)
              echo "  ✅ Trained model: $SIZE"
            else
              echo "  ❌ No trained model"
            fi
            echo ""
            
            echo "🔑 API Key:"
            if [ -n "$GEMINI_API_KEY" ]; then
              echo "  ✅ Set"
            else
              echo "  ❌ Not set"
            fi
            echo ""
            
            echo "🖥️  System:"
            echo "  Python: $(${pythonEnv}/bin/python --version)"
            echo "  CUDA: $(${pythonEnv}/bin/python -c 'import torch; print("Available" if torch.cuda.is_available() else "Not available")' 2>/dev/null || echo "N/A")"
          '';

          # Clean project
          ai-clean = makeScript "ai-clean" ''
            echo "🧹 Cleaning project..."
            
            read -p "Remove training data? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
              rm -rf data/*.jsonl data/*.json
              echo "  ✓ Removed training data"
            fi
            
            read -p "Remove trained models? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
              rm -rf models/
              echo "  ✓ Removed models"
            fi
            
            read -p "Remove cache? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
              rm -rf .cache/
              echo "  ✓ Removed cache"
            fi
            
            # Always clean Python artifacts
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -type f -name "*.pyc" -delete 2>/dev/null || true
            echo "  ✓ Removed Python artifacts"
            
            echo "✅ Cleaned!"
          '';

          # Show help
          ai-help = makeScript "ai-help" ''
            echo "🤖 AI CLI Development Commands"
            echo "=============================="
            echo ""
            echo "🚀 Getting Started:"
            echo "  ai-init              Initialize project structure"
            echo "  ai-status            Show project status"
            echo "  ai-design            Design AI personality (interactive)"
            echo "  ai-test-prompt       Test system prompt"
            echo ""
            echo "📊 Data & Training:"
            echo "  ai-generate-data     Generate training data"
            echo "  ai-train             Train the model"
            echo "  ai-test              Test model (interactive)"
            echo "  ai-test --auto       Run automated tests"
            echo ""
            echo "💬 Using Your AI:"
            echo "  ai-chat              Start interactive chat"
            echo "  ai-ask 'question'    Ask a quick question"
            echo ""
            echo "🔧 Maintenance:"
            echo "  ai-clean             Clean build artifacts"
            echo "  ai-help              Show this help"
            echo ""
            echo "📝 Configuration:"
            echo "  Edit config.nix to change AI personality, model, training params"
            echo "  Changes take effect immediately in nix develop shell"
            echo ""
            echo "🔑 Environment Variables:"
            echo "  GEMINI_API_KEY       API key for data generation (required)"
            echo "  CUDA_VISIBLE_DEVICES GPU selection (optional)"
            echo ""
            echo "💡 Quick Start Example:"
            echo "  export GEMINI_API_KEY='your-key-here'"
            echo "  ai-init"
            echo "  ai-generate-data"
            echo "  ai-train"
            echo "  ai-chat"
          '';
        };

        # Combine all scripts
        allScripts = pkgs.symlinkJoin {
          name = "ai-cli-scripts";
          paths = pkgs.lib.attrValues scripts;
        };

      in {
        # Main development shell
        devShells.default = pkgs.mkShell {
          name = "ai-cli-dev";
          
          buildInputs = [
            pythonEnv
            allScripts
            
            # Build tools
            pkgs.gcc
            pkgs.git
            
            # CUDA (if available)
            pkgs.cudaPackages.cudatoolkit
            
            # Nix tools
            pkgs.nixpkgs-fmt
            pkgs.alejandra
            
            # Utilities
            pkgs.jq
            pkgs.tree
          ];
          
          shellHook = ''
            # Set project root
            export PRJ_ROOT="$(pwd)"
            
            # Python paths
            export PYTHONPATH="$PRJ_ROOT:$PYTHONPATH"
            export PYTHONUNBUFFERED=1
            export PYTHONDONTWRITEBYTECODE=1
            
            # AI/ML paths
            export TRANSFORMERS_CACHE="$PRJ_ROOT/.cache/transformers"
            export HF_HOME="$PRJ_ROOT/.cache/huggingface"
            export HF_HUB_CACHE="$PRJ_ROOT/.cache/huggingface/hub"
            
            # Configuration
            export AI_CONFIG_FILE="$PRJ_ROOT/config.nix"
            export BASE_MODEL="${config.model.baseModel}"
            
            # Create directories
            mkdir -p .cache/{transformers,huggingface/hub}
            
            # Welcome message
            echo ""
            echo "╔════════════════════════════════════════════╗"
            echo "║  🤖 AI CLI Development Environment       ║"
            echo "╚════════════════════════════════════════════╝"
            echo ""
            echo "📍 Project: $PRJ_ROOT"
            echo "🐍 Python: $(python --version)"
            echo "🔧 Base Model: ${config.model.baseModel}"
            echo ""
            
            # Check CUDA
            if python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
              echo "🚀 CUDA: Available"
            else
              echo "💻 CUDA: Not available (CPU mode)"
            fi
            echo ""
            
            # Quick status
            ai-status
            
            echo ""
            echo "💡 Type 'ai-help' for available commands"
            echo ""
          '';
        };

        # Minimal shell for CI/CD
        devShells.ci = pkgs.mkShell {
          buildInputs = [ pythonEnv pkgs.git ];
          shellHook = ''
            export PYTHONPATH="$(pwd):$PYTHONPATH"
            export TRANSFORMERS_CACHE=".cache/transformers"
          '';
        };

        # Shell for data generation only
        devShells.data = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            scripts.ai-generate-data
            scripts.ai-status
          ];
          shellHook = ''
            echo "📊 Data Generation Shell"
            echo "Run: ai-generate-data"
          '';
        };

        # Shell for training only
        devShells.train = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.cudaPackages.cudatoolkit
            scripts.ai-train
            scripts.ai-status
          ];
          shellHook = ''
            echo "🏋️  Training Shell"
            echo "Run: ai-train"
          '';
        };
      }
    );
}
