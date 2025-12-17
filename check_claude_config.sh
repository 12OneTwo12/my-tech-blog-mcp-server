#!/bin/bash
# Claude Code (CLI) MCP 설정 확인 스크립트

echo "====================================="
echo "Claude Code MCP 설정 확인"
echo "====================================="
echo ""

CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"

echo "설정 파일 위치:"
echo "  $CLAUDE_CONFIG"
echo ""

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✓ 설정 파일 존재"
    echo ""
    echo "현재 설정 내용:"
    echo "-----------------------------------"
    cat "$CLAUDE_CONFIG"
    echo ""
    echo "-----------------------------------"
    echo ""

    # my-tech-blog 서버 확인
    if grep -q "my-tech-blog" "$CLAUDE_CONFIG"; then
        echo "✓ my-tech-blog 서버 설정 발견"
        echo ""
        echo "MCP 서버 목록:"
        grep -o '"[^"]*":' "$CLAUDE_CONFIG" | grep -v mcpServers | sed 's/"://g; s/"//g' | sed 's/^/  - /'
    else
        echo "✗ my-tech-blog 서버 설정이 없습니다"
        echo ""
        echo "설치 스크립트를 실행하세요:"
        echo "  ./install.sh"
    fi
else
    echo "✗ 설정 파일이 없습니다"
    echo ""
    echo "설치 스크립트를 실행하세요:"
    echo "  ./install.sh"
fi

echo ""
