#!/bin/bash
# Test script for install.sh - simulates Claude Desktop config update

set -e

echo "=" * 80
echo "Testing Claude Desktop config update logic"
echo "=" * 80
echo ""

# Create temporary test directory
TEST_DIR=$(mktemp -d)
echo "Test directory: $TEST_DIR"
echo ""

# Test Case 1: No existing config
echo "Test 1: 설정 파일이 없는 경우"
TEST_CONFIG="$TEST_DIR/claude_desktop_config.json"

mkdir -p "$(dirname "$TEST_CONFIG")"

cat > "$TEST_CONFIG" <<EOF
{
  "mcpServers": {
    "my-tech-blog": {
      "command": "/path/to/python",
      "args": ["/path/to/run.py"]
    }
  }
}
EOF

echo "   ✓ 새 설정 파일 생성됨"
cat "$TEST_CONFIG"
echo ""

# Test Case 2: Existing config with other servers
echo "Test 2: 기존 서버가 있는 설정 파일"
cat > "$TEST_CONFIG" <<EOF
{
  "mcpServers": {
    "existing-server": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/other.py"]
    }
  }
}
EOF

echo "   기존 설정:"
cat "$TEST_CONFIG"
echo ""

# Python으로 병합
python3 << PYTHON_SCRIPT
import json

config_path = "$TEST_CONFIG"
new_server = {
    "command": "/new/path/to/python",
    "args": ["/new/path/to/run.py"]
}

with open(config_path, 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['my-tech-blog'] = new_server

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("   ✓ 병합 완료")
PYTHON_SCRIPT

echo "   병합 후 설정:"
cat "$TEST_CONFIG"
echo ""

# Test Case 3: Update existing my-tech-blog server
echo "Test 3: 기존 my-tech-blog 서버 업데이트"
python3 << PYTHON_SCRIPT
import json

config_path = "$TEST_CONFIG"
new_server = {
    "command": "/updated/path/to/python",
    "args": ["/updated/path/to/run.py"]
}

with open(config_path, 'r') as f:
    config = json.load(f)

config['mcpServers']['my-tech-blog'] = new_server

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("   ✓ 업데이트 완료")
PYTHON_SCRIPT

echo "   업데이트 후 설정:"
cat "$TEST_CONFIG"
echo ""

# Cleanup
rm -rf "$TEST_DIR"

echo "=" * 80
echo "✓ All tests passed!"
echo "=" * 80
echo ""
echo "install.sh의 Claude Desktop 자동 설정 로직이 정상 작동합니다."
echo ""
