#!/bin/bash

echo "🚀 Multi-Agent Creativity System - Setup Script"
echo "================================================"
echo ""

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Conda detected"
    
    # Check if 'graph' environment exists
    if conda env list | grep -q "graph"; then
        echo "✅ Conda environment 'graph' found"
        echo "   Activating environment..."
        # Note: In scripts, conda activate doesn't persist
        # User needs to manually activate
    else
        echo "⚠️  Conda environment 'graph' not found"
        echo "   You can create it with: conda create -n graph python=3.10"
    fi
else
    echo "⚠️  Conda not detected. Using system Python."
fi

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p data/vectors
mkdir -p reports
mkdir -p ui/dashboard

echo ""
echo "🔑 Checking for API keys..."
if [ -f .env ]; then
    echo "✅ .env file found"
    
    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo "✅ API keys configured"
    else
        echo "⚠️  No ANTHROPIC_API_KEY found in .env file"
        echo "   Please add ANTHROPIC_API_KEY to .env (required for Claude Sonnet 4.5)"
    fi
else
    echo "⚠️  .env file not found"
    echo "   Creating template .env file..."
    
    cat > .env << 'EOL'
# LLM API Keys (Anthropic required for Claude Sonnet 4.5)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Configuration
MAX_ITERATIONS=10
TOP_K_IDEAS=5
SIMILARITY_THRESHOLD=0.85

# Scoring Weights (should sum to ~1.0)
NOVELTY_WEIGHT=0.3
FEASIBILITY_WEIGHT=0.3
MARKET_FIT_WEIGHT=0.2
VIABILITY_WEIGHT=0.2

# Model Selection (all agents use Claude Sonnet 4.5 by default)
# GENERATOR_MODEL=claude-sonnet-4.5-20250514
# CRITIC_MODEL=claude-sonnet-4.5-20250514
EOL
    
    echo "   📝 Template .env created. Please edit it with your API keys."
fi

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Activate conda environment: conda activate graph"
echo "  3. Run an example: python example.py"
echo "  4. Or generate ideas: python main.py generate --domain GRC --num-ideas 5"
echo ""
echo "For full documentation, see README.md"
echo "================================================"

