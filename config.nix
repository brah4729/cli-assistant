# config.nix - Simple configuration for CodeBuddy

{
  # Model settings
  model = {
    baseModel = "microsoft/phi-2";  # Fast, small, capable
    # Alternatives: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
  };

  # Training settings
  training = {
    numEpochs = 3;
    batchSize = 4;  # Lower if you run out of memory
    learningRate = 2e-4;
    maxSeqLength = 512;
  };

  # CLI name
  cli = {
    name = "cli-assitant";
  };
}