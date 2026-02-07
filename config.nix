# config.nix
# Declarative configuration for the AI CLI project
# This file contains all project settings in a pure, reproducible way

{
  # Project Metadata
  project = {
    name = "codebuddy";
    version = "0.1.0";
    description = "Custom AI coding companion";
    author = "Your Name";
  };

  # Model Configuration
  model = {
    # Base model selection
    baseModel = "microsoft/phi-2";
    # Alternatives:
    # baseModel = "TinyLlama/TinyLlama-1.1B-Chat-v1.0";
    # baseModel = "mistralai/Mistral-7B-v0.1";
    
    # Model storage
    cacheDir = ".cache/transformers";
    saveDir = "models";
  };

  # Training Configuration
  training = {
    numEpochs = 3;
    batchSize = 4;
    learningRate = 2e-4;
    maxSeqLength = 512;
    warmupSteps = 50;
    saveSteps = 100;
    loggingSteps = 10;
    
    # LoRA (Low-Rank Adaptation) settings
    lora = {
      r = 16;
      loraAlpha = 32;
      loraDropout = 0.05;
      targetModules = [ "q_proj" "k_proj" "v_proj" "o_proj" ];
    };
    
    # Quantization settings
    quantization = {
      load4bit = true;
      use8bit = false;
      computeDtype = "float16";
    };
  };

  # Data Generation Configuration
  dataGeneration = {
    numExamples = 100;
    minExamples = 50;
    maxExamples = 1000;
    
    # API settings
    apiModel = "gemini-1.5-flash";
    rateLimit = {
      requestsPerMinute = 15;
      delayBetweenRequests = 1; # seconds
    };
  };

  # Inference Configuration
  inference = {
    maxNewTokens = 256;
    temperature = 0.7;
    topP = 0.9;
    repetitionPenalty = 1.1;
    doSample = true;
  };

  # System Prompt (AI Personality)
  systemPrompt = ''
    You are a warm, enthusiastic AI coding companion named CodeBuddy.

    Your core traits:
    - Genuinely excited about helping people learn and build things
    - Empathetic and patient when people are struggling
    - Celebratory and encouraging when they succeed
    - Natural and conversational, never robotic or formal
    - Concise but thorough (aim for 2-4 paragraphs)

    Your approach to helping:
    - Start with the most practical, actionable solution
    - Include concrete code examples when relevant
    - Explain the "why" behind solutions, not just the "how"
    - Acknowledge when something is genuinely tricky
    - Ask clarifying questions when needed
    - Use light humor to keep things enjoyable
    - Use 1-2 emojis per response for warmth (not overboard!)

    Your values:
    - Everyone can learn to code with the right support
    - There are no "stupid questions"
    - Mistakes are learning opportunities
    - Building things is more important than perfection
    - Understanding beats memorization

    Remember: You're a supportive companion on their coding journey, not just a tool!
  '';

  # CLI Configuration
  cli = {
    name = "codebuddy";
    defaultCommand = "chat";
    colors = {
      primary = "cyan";
      success = "green";
      warning = "yellow";
      error = "red";
      info = "blue";
    };
  };

  # Directory Structure
  directories = {
    data = "data";
    models = "models";
    logs = "logs";
    cache = ".cache";
    src = "src";
  };

  # Development Settings
  development = {
    pythonVersion = "3.11";
    cudaSupport = true;
    formatOnSave = true;
    
    # Testing
    runTestsOnBuild = false;
    
    # Linting
    enableLinting = true;
    linters = [ "pylint" "black" ];
  };

  # Deployment Settings
  deployment = {
    buildExecutable = true;
    includeModels = false; # Models are too large, download separately
    targetPlatforms = [ "x86_64-linux" "aarch64-darwin" "x86_64-darwin" ];
  };
}
