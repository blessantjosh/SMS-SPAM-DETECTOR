#!/bin/bash
# Test script to verify frontend-backend integration

echo "========================================"
echo "CyberSentinel Integration Test"
echo "========================================"
echo ""

# Test 1: Backend Health
echo "1. Testing Backend Health..."
response=$(curl -s http://localhost:8000/api/health)
if [ $? -eq 0 ]; then
    echo "   ✅ Backend is running"
    echo "   Response: $response"
else
    echo "   ❌ Backend is not responding"
    exit 1
fi
echo ""

# Test 2: System Status
echo "2. Testing System Status API..."
response=$(curl -s http://localhost:8000/api/system/status)
if [ $? -eq 0 ]; then
    echo "   ✅ System Status API working"
    echo "   Response: $response"
else
    echo "   ❌ System Status API failed"
fi
echo ""

# Test 3: Dashboard Stats
echo "3. Testing Dashboard Stats API..."
response=$(curl -s http://localhost:8000/api/dashboard/stats)
if [ $? -eq 0 ]; then
    echo "   ✅ Dashboard Stats API working"
    echo "   Response: $response"
else
    echo "   ❌ Dashboard Stats API failed"
fi
echo ""

# Test 4: Model Performance
echo "4. Testing Model Performance API..."
response=$(curl -s http://localhost:8000/api/model/performance)
if [ $? -eq 0 ]; then
    echo "   ✅ Model Performance API working"
    echo "   Response: $response"
else
    echo "   ❌ Model Performance API failed"
fi
echo ""

# Test 5: SMS Analysis
echo "5. Testing SMS Analysis API..."
response=$(curl -s -X POST http://localhost:8000/api/sms/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"URGENT: Your account will be blocked. Click here now!"}')
if [ $? -eq 0 ]; then
    echo "   ✅ SMS Analysis API working"
    echo "   Response: $response"
else
    echo "   ❌ SMS Analysis API failed"
fi
echo ""

# Test 6: Frontend
echo "6. Testing Frontend Server..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4200)
if [ "$response" = "200" ]; then
    echo "   ✅ Frontend is running on http://localhost:4200"
else
    echo "   ⚠️  Frontend might not be running (HTTP $response)"
    echo "   Start it with: cd cybersentinel-dashboard && npm start"
fi
echo ""

echo "========================================"
echo "Integration Test Complete!"
echo "========================================"
echo ""
echo "Frontend: http://localhost:4200"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
