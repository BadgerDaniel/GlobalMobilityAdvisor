#!/bin/bash

# Global IQ Mobility Advisor - Docker Deployment Script
echo "🚀 Global IQ Mobility Advisor - Docker Deployment"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Please set your OPENAI_API_KEY in the .env file"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting Global IQ application..."
docker-compose up --build -d

# Wait for container to be ready
echo "⏳ Waiting for application to start..."
sleep 10

# Check if container is running
if docker ps | grep -q "global-iq-mobility-advisor"; then
    echo ""
    echo "🎉 SUCCESS! Global IQ Mobility Advisor is now running!"
    echo ""
    echo "📱 Access your application at: http://localhost:8000"
    echo ""
    echo "🔐 Login Credentials:"
    echo "   Demo User: demo / demo"
    echo "   Admin User: admin / admin123"
    echo "   Employee: employee / employee123"
    echo "   HR Manager: hr_manager / hr2024"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs: docker logs global-iq-mobility-advisor"
    echo "   Stop app: docker-compose down"
    echo "   Restart: docker-compose restart"
    echo ""
else
    echo "❌ Failed to start the application. Check logs:"
    docker logs global-iq-mobility-advisor
fi
