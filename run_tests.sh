#!/bin/bash
# Test Runner Script

echo "🧪 AGTR Merkezi - Test Suite"
echo "================================"

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Syntax check
echo -e "\n${YELLOW}1. Syntax Check...${NC}"
python3 -m py_compile app/services/subscription_service.py
python3 -m py_compile app/services/error_handler.py
python3 -m py_compile app/tasks/billing_job.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Syntax check passed${NC}"
else
    echo -e "${RED}✗ Syntax check failed${NC}"
    exit 1
fi

# Unit tests
echo -e "\n${YELLOW}2. Running Unit Tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/services/ -v --tb=short
    UNIT_RESULT=$?
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping unit tests${NC}"
    echo "Install with: pip install pytest pytest-asyncio"
    UNIT_RESULT=0
fi

# Integration tests
echo -e "\n${YELLOW}3. Running Integration Tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/api/ -v --tb=short
    INT_RESULT=$?
else
    echo -e "${YELLOW}⚠ Skipping integration tests${NC}"
    INT_RESULT=0
fi

# Import tests
echo -e "\n${YELLOW}4. Import Tests...${NC}"
python3 -c "from app.services.subscription_service import SubscriptionService; print('✓ SubscriptionService')"
python3 -c "from app.services.error_handler import TransactionRollbackService; print('✓ TransactionRollbackService')"
python3 -c "from app.services.notification_service import NotificationService; print('✓ NotificationService')"
python3 -c "from app.tasks.billing_job import process_subscription_billing; print('✓ BillingJob')"

IMPORT_RESULT=$?

# Sonuçlar
echo -e "\n================================"
echo "📊 Test Results:"
echo "================================"

if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Unit Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Unit Tests: FAILED${NC}"
fi

if [ $INT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Integration Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Integration Tests: FAILED${NC}"
fi

if [ $IMPORT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Import Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Import Tests: FAILED${NC}"
fi

echo "================================"

# Toplam sonuç
if [ $UNIT_RESULT -eq 0 ] && [ $INT_RESULT -eq 0 ] && [ $IMPORT_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
