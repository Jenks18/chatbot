#!/bin/bash

# Health check script for ToxicoGPT
# Run this to verify all components are working

echo "======================================"
echo "🔍 ToxicoGPT Health Check"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    SERVICE_NAME=$1
    CONTAINER_NAME=$2
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo -e "${GREEN}✓${NC} $SERVICE_NAME is running"
        return 0
    else
        echo -e "${RED}✗${NC} $SERVICE_NAME is NOT running"
        return 1
    fi
}

check_url() {
    URL=$1
    SERVICE_NAME=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "200\|404"; then
        echo -e "${GREEN}✓${NC} $SERVICE_NAME is responding at $URL"
        return 0
    else
        echo -e "${RED}✗${NC} $SERVICE_NAME is NOT responding at $URL"
        return 1
    fi
}

# Check Docker containers
echo "📦 Checking Docker containers..."
check_service "PostgreSQL Database" "toxicology-db"
check_service "Backend API" "toxicology-backend"
check_service "Frontend" "toxicology-frontend"
check_service "Model Server" "toxicology-model"
echo ""

# Check HTTP endpoints
echo "🌐 Checking HTTP endpoints..."
check_url "http://localhost:8000/health" "Backend Health"
check_url "http://localhost:8000/docs" "API Documentation"
check_url "http://localhost:3000" "Frontend"
check_url "http://localhost:11434/api/tags" "Model Server"
echo ""

# Check if model is downloaded
echo "🤖 Checking AI model..."
if docker exec toxicology-model ollama list 2>/dev/null | grep -q "llama3\|mistral\|meditron"; then
    echo -e "${GREEN}✓${NC} AI model is downloaded"
    docker exec toxicology-model ollama list | tail -n +2
else
    echo -e "${YELLOW}⚠${NC}  No AI model found. Run: ./setup-model.sh"
fi
echo ""

# Check database connection
echo "💾 Checking database..."
if docker exec toxicology-db psql -U toxgpt_user -d toxicology_gpt -c "SELECT 1;" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Database is accessible"
    
    # Count logs
    LOG_COUNT=$(docker exec toxicology-db psql -U toxgpt_user -d toxicology_gpt -t -c "SELECT COUNT(*) FROM chat_logs;" 2>/dev/null | tr -d ' ')
    SESSION_COUNT=$(docker exec toxicology-db psql -U toxgpt_user -d toxicology_gpt -t -c "SELECT COUNT(*) FROM sessions;" 2>/dev/null | tr -d ' ')
    
    echo -e "  Total chat logs: $LOG_COUNT"
    echo -e "  Total sessions: $SESSION_COUNT"
else
    echo -e "${RED}✗${NC} Cannot connect to database"
fi
echo ""

# Check disk space
echo "💿 Checking disk usage..."
docker system df | head -n 5
echo ""

# Test API endpoint
echo "🧪 Testing API endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, test message"}' 2>/dev/null)

if echo "$RESPONSE" | grep -q "answer"; then
    echo -e "${GREEN}✓${NC} Chat API is working"
else
    echo -e "${RED}✗${NC} Chat API test failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Summary
echo "======================================"
echo "📊 Summary"
echo "======================================"
echo ""
echo "Services Status:"
docker-compose ps
echo ""
echo "Quick Links:"
echo "  Chat:  http://localhost:3000"
echo "  Admin: http://localhost:3000/admin"
echo "  API:   http://localhost:8000/docs"
echo ""
echo "Commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Restart:       docker-compose restart"
echo "  Stop:          ./stop.sh"
echo ""
