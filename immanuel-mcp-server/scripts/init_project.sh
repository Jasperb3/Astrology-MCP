#!/bin/bash

# Initialize the Immanuel MCP Server project

set -e

echo "🚀 Initializing Immanuel MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate
uv pip install -e .

# Create environment file
if [ ! -f .env ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    echo "✓ Created .env file. Please review and update the settings."
else
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✓ Created logs directory"

# Generate SSL certificates for development
if [ ! -f ssl/cert.pem ]; then
    echo "🔒 Generating SSL certificates for development..."
    ./scripts/generate_ssl.sh
else
    echo "✓ SSL certificates already exist"
fi

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
pytest --tb=short -v

# Check code quality
echo "🔍 Checking code quality..."
ruff app/ tests/ || echo "⚠️  Linting issues found (non-critical)"
mypy app/ || echo "⚠️  Type checking issues found (non-critical)"

echo ""
echo "✅ Immanuel MCP Server initialized successfully!"
echo ""
echo "🚀 Quick start:"
echo "   1. Review and update .env configuration"
echo "   2. Start development server:"
echo "      make dev"
echo "   3. Test the API:"
echo "      make health"
echo "   4. View API documentation:"
echo "      http://localhost:8000/docs"
echo ""
echo "🐳 Docker commands:"
echo "   make docker-build   # Build Docker image"
echo "   make docker-dev     # Run development environment"
echo "   make docker-prod    # Run production environment"
echo ""
echo "📖 More commands available in Makefile:"
echo "   make help"