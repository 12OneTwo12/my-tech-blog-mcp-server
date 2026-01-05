#!/bin/bash
# Installation script for My Tech Blog MCP Server (Claude Code CLI)

set -e

echo "====================================="
echo "My Tech Blog MCP Server 설치"
echo "====================================="
echo ""

# Check Python version
echo "1. Python 버전 확인..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python 버전: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "   오류: Python 3.10 이상이 필요합니다."
    exit 1
fi
echo "   ✓ Python 버전 확인 완료"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "2. 가상 환경 생성..."
    python3 -m venv venv
    echo "   ✓ 가상 환경 생성 완료"
    echo ""
else
    echo "2. 기존 가상 환경 발견"
    echo "   ✓ 가상 환경 확인 완료"
    echo ""
fi

# Activate virtual environment
echo "3. 가상 환경 활성화..."
source venv/bin/activate
echo "   ✓ 가상 환경 활성화 완료"
echo ""

# Install dependencies
echo "4. 의존성 패키지 설치..."
pip install -r requirements.txt
echo "   ✓ 의존성 설치 완료"
echo ""

# Make run.py executable
echo "5. 실행 권한 설정..."
chmod +x run.py
echo "   ✓ 실행 권한 설정 완료"
echo ""

# Get current directory
CURRENT_DIR=$(pwd)

# Generate Claude Desktop config
echo "6. Claude Desktop 설정 파일 생성..."
cat > claude_desktop_config.json <<EOF
{
  "mcpServers": {
    "my-tech-blog": {
      "command": "$CURRENT_DIR/venv/bin/python",
      "args": [
        "$CURRENT_DIR/run.py"
      ]
    }
  }
}
EOF
echo "   ✓ 설정 파일 생성 완료: claude_desktop_config.json"
echo ""

# Auto-configure Claude Code (CLI)
CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"

echo "7. Claude Code MCP 서버 설정 중..."

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "   기존 설정 발견"
    echo "   백업 생성 중..."
    cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   ✓ 백업 완료"

    # Python으로 JSON 병합
    python3 << PYTHON_SCRIPT
import json
import sys

config_path = "$CLAUDE_CONFIG"
new_server = {
    "command": "$CURRENT_DIR/venv/bin/python",
    "args": ["$CURRENT_DIR/run.py"]
}

try:
    # 기존 설정 읽기
    with open(config_path, 'r') as f:
        config = json.load(f)

    # mcpServers가 없으면 생성
    if 'mcpServers' not in config:
        config['mcpServers'] = {}

    # my-tech-blog 서버 추가/업데이트
    config['mcpServers']['my-tech-blog'] = new_server

    # 설정 저장
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("   ✓ Claude Code 설정 업데이트 완료")
except Exception as e:
    print(f"   ✗ 오류: {e}")
    sys.exit(1)
PYTHON_SCRIPT

else
    echo "   설정 파일이 없습니다."
    echo "   디렉토리 생성 중..."
    mkdir -p "$(dirname "$CLAUDE_CONFIG")"
    cp claude_desktop_config.json "$CLAUDE_CONFIG"
    echo "   ✓ 새 설정 파일 생성 완료"
fi
echo ""

# Register ALL MCP servers from JSON config to Claude Code
echo "8. Claude Code에 모든 MCP 서버 등록 중..."
if command -v claude &> /dev/null; then
    # JSON 파일에 있는 모든 서버를 claude mcp에 등록
    python3 << PYTHON_SCRIPT
import json
import subprocess
import sys

config_path = "$CLAUDE_CONFIG"

try:
    with open(config_path, 'r') as f:
        config = json.load(f)

    servers = config.get('mcpServers', {})
    if not servers:
        print("   ⚠ 등록할 MCP 서버가 없습니다.")
        sys.exit(0)

    print(f"   {len(servers)}개의 MCP 서버 등록 중...")

    for server_name, server_config in servers.items():
        # 기존 서버 제거 (있다면, 에러 무시)
        subprocess.run(
            ['claude', 'mcp', 'remove', server_name],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )

        # 서버 재등록
        cmd = [
            'claude', 'mcp', 'add',
            '--transport', 'stdio',
            server_name,
            '--',
            server_config['command']
        ] + server_config['args']

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ {server_name} 등록 완료")
        else:
            print(f"   ✗ {server_name} 등록 실패: {result.stderr.strip()}")

except Exception as e:
    print(f"   ✗ 오류: {e}")
    sys.exit(1)
PYTHON_SCRIPT

else
    echo "   ⚠ claude 명령어를 찾을 수 없습니다."
    echo "   수동으로 등록하세요:"
    echo "   claude mcp add --transport stdio my-tech-blog -- $CURRENT_DIR/venv/bin/python $CURRENT_DIR/run.py"
fi
echo ""

echo "====================================="
echo "설치 완료!"
echo "====================================="
echo ""
echo "설정 위치: $CLAUDE_CONFIG"
echo ""
echo "다음 단계:"
echo "1. 새 Claude Code 세션 시작"
echo "   (현재 세션을 종료하고 새로 시작하면 MCP 도구 사용 가능)"
echo ""
echo "2. 테스트:"
echo '   "내가 과거에 Kubernetes 도입할 때 어떤 문제를 겪었어?"'
echo ""
echo "3. MCP 서버 확인:"
echo "   claude mcp list"
echo ""
