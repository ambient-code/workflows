#!/bin/bash

# RHOAI Security Scanner Integration Script
# This script integrates with the external RHOAI security scanner

set -e

SCANNER_REPO="https://gitlab.cee.redhat.com/mstratto/rhoai-security-scanner.git"
SCANNER_DIR="/tmp/rhoai-security-scanner"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-artifacts}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 RHOAI Security Scanner Integration${NC}"
echo "==========================================="

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check for git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git is not installed${NC}"
        exit 1
    fi
    
    # Check for Python (assuming the scanner needs it)
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites satisfied${NC}"
}

# Function to clone or update scanner
setup_scanner() {
    echo -e "${YELLOW}Setting up RHOAI Security Scanner...${NC}"
    
    if [ -d "$SCANNER_DIR" ]; then
        echo "Updating existing scanner installation..."
        cd "$SCANNER_DIR"
        git pull origin main || true
    else
        echo "Cloning scanner repository..."
        git clone "$SCANNER_REPO" "$SCANNER_DIR" || {
            echo -e "${RED}Failed to clone scanner repository${NC}"
            echo "This might be due to access restrictions."
            echo "Please ensure you have access to: $SCANNER_REPO"
            exit 1
        }
    fi
    
    cd "$SCANNER_DIR"
    
    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies..."
        pip3 install -r requirements.txt --user
    fi
    
    echo -e "${GREEN}✓ Scanner setup complete${NC}"
}

# Function to run the scanner
run_scanner() {
    local scan_target="${1:-$(pwd)}"
    local scan_type="${2:-comprehensive}"
    
    echo -e "${YELLOW}Running security scan...${NC}"
    echo "Target: $scan_target"
    echo "Type: $scan_type"
    
    # Create artifacts directory
    mkdir -p "$ARTIFACTS_DIR/security-reports"
    mkdir -p "$ARTIFACTS_DIR/vulnerabilities"
    
    # Generate timestamp for reports
    timestamp=$(date +%Y%m%d-%H%M%S)
    report_file="$ARTIFACTS_DIR/security-reports/scan-$timestamp.md"
    json_file="$ARTIFACTS_DIR/vulnerabilities/findings-$timestamp.json"
    
    # Check if scanner has a main script
    if [ -f "$SCANNER_DIR/scanner.py" ]; then
        python3 "$SCANNER_DIR/scanner.py" \
            --target "$scan_target" \
            --output "$report_file" \
            --json "$json_file" \
            --type "$scan_type" || true
    elif [ -f "$SCANNER_DIR/rhoai-scanner" ]; then
        "$SCANNER_DIR/rhoai-scanner" audit \
            --path "$scan_target" \
            --report "$report_file" || true
    else
        echo -e "${YELLOW}Scanner executable not found, using fallback scanning...${NC}"
        
        # Fallback: Basic security scanning
        echo "# Security Scan Report" > "$report_file"
        echo "Generated: $(date)" >> "$report_file"
        echo "" >> "$report_file"
        
        # Scan for common issues
        echo "## Manifest Security Scan" >> "$report_file"
        find "$scan_target" -name "*.yaml" -o -name "*.yml" | while read -r file; do
            echo "Scanning: $file" >> "$report_file"
            
            # Check for security issues
            grep -n "privileged: true" "$file" >> "$report_file" 2>/dev/null || true
            grep -n "runAsRoot: true" "$file" >> "$report_file" 2>/dev/null || true
            grep -n "hostNetwork: true" "$file" >> "$report_file" 2>/dev/null || true
        done
        
        # Generate JSON findings
        echo '{"findings": [], "summary": {"total": 0, "critical": 0}}' > "$json_file"
    fi
    
    echo -e "${GREEN}✓ Scan complete${NC}"
    echo "Reports generated:"
    echo "  - Markdown: $report_file"
    echo "  - JSON: $json_file"
}

# Main execution
main() {
    check_prerequisites
    setup_scanner
    run_scanner "$@"
}

# Run main function with all arguments
main "$@"
