{
  description = "CodeBuddy - Your warm & fuzzy AI companion";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        config.cudaSupport = false;
        config.rocmSupport = false;
      };

      # Python with essential packages
      python = pkgs.python311.withPackages (ps: with ps; [
        # Core ML
        ps.torch
        transformers
        accelerate
        huggingface-hub
        datasets  # Required by trainer.py

        # CLI
        click
        rich

        # Image support
        pillow

        # Utilities
        numpy
        tqdm
        pyyaml
      ]);

      # Shell script helper
      makeScript = name: text: pkgs.writeShellScriptBin name ''
        set -e
        cd "''${PRJ_ROOT:-$PWD}"
        ${text}
      '';

      # Core commands
      codebuddy = makeScript "codebuddy" ''
        ${python}/bin/python -m src.cli "$@"
      '';

      ai-generate-data = makeScript "ai-generate-data" ''
        ${python}/bin/python -m src.data_generator "$@"
      '';

      ai-train = makeScript "ai-train" ''
        ${python}/bin/python -m src.trainer data/training_data.jsonl
      '';

      ai-chat = makeScript "ai-chat" ''
        ${python}/bin/python -m src.cli chat
      '';

      ai-ask = makeScript "ai-ask" ''
        ${python}/bin/python -m src.cli ask "$@"
      '';

      ai-clean = makeScript "ai-clean" ''
        rm -rf __pycache__ src/__pycache__ .cache
        find . -name "*.pyc" -delete
      '';

      ai-help = makeScript "ai-help" ''
        echo "Commands: codebuddy, ai-generate-data, ai-train, ai-chat, ai-ask, ai-clean"
      '';

    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          python
          codebuddy
          ai-generate-data
          ai-train
          ai-chat
          ai-ask
          ai-clean
          ai-help
          pkgs.git
        ];

        shellHook = ''
          export PRJ_ROOT="$PWD"
          export PYTHONPATH="$PWD:$PYTHONPATH"
          export TRANSFORMERS_CACHE="$PWD/.cache/transformers"
          export HF_HOME="$PWD/.cache/huggingface"
          export AI_MODEL_PATH="$PWD/models/final-model"
          echo "CodeBuddy ready! Run: ai-help"
        '';
      };
    };
}
