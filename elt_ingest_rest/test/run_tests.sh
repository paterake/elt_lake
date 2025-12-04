#!/bin/bash
# Test runner script for REST API Ingester

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting REST API Ingester Test Suite${NC}"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")/.." || exit 1

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest"
    exit 1
fi

# Run tests based on argument
case "$1" in
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest test/test_pagination_types.py -v
        ;;
    "no-pagination")
        echo -e "${GREEN}Running no pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestNoPagination -v
        ;;
    "offset-limit")
        echo -e "${GREEN}Running offset/limit pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestOffsetLimitPagination -v
        ;;
    "page-number")
        echo -e "${GREEN}Running page number pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestPageNumberPagination -v
        ;;
    "link-header")
        echo -e "${GREEN}Running link header pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestLinkHeaderPagination -v
        ;;
    "next-url")
        echo -e "${GREEN}Running next URL pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestNextUrlPagination -v
        ;;
    "cursor")
        echo -e "${GREEN}Running cursor pagination tests...${NC}"
        pytest test/test_pagination_types.py::TestCursorPagination -v
        ;;
    "edge-cases")
        echo -e "${GREEN}Running edge case tests...${NC}"
        pytest test/test_pagination_types.py::TestEdgeCases -v
        ;;
    "batch")
        echo -e "${GREEN}Running batch save tests...${NC}"
        pytest test/test_pagination_types.py::TestBatchSaving -v
        ;;
    "extraction")
        echo -e "${GREEN}Running data extraction tests...${NC}"
        pytest test/test_pagination_types.py::TestDataExtraction -v
        ;;
    "coverage")
        echo -e "${GREEN}Running tests with coverage...${NC}"
        pytest test/test_pagination_types.py --cov=elt_ingest_rest --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}Coverage report saved to htmlcov/index.html${NC}"
        ;;
    "quick")
        echo -e "${GREEN}Running quick test (no pagination only)...${NC}"
        pytest test/test_pagination_types.py::TestNoPagination::test_jsonplaceholder_single_post -v
        ;;
    *)
        echo "Usage: $0 {all|no-pagination|offset-limit|page-number|link-header|next-url|cursor|edge-cases|batch|extraction|coverage|quick}"
        echo ""
        echo "Examples:"
        echo "  $0 all              # Run all tests"
        echo "  $0 offset-limit     # Run offset/limit pagination tests"
        echo "  $0 coverage         # Run tests with coverage report"
        echo "  $0 quick            # Run single quick test"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Test run complete!${NC}"
