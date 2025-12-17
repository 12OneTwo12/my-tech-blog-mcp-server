# 빠른 시작 가이드 - Claude Code (CLI)

## 20초 안에 시작하기

### 1. 설치 (15초)

```bash
cd /Users/jeongjeong-il/Desktop/projects/my-tech-blog-mcp-server
./install.sh
```

**자동으로 완료됩니다:**
- ✅ 가상 환경 생성
- ✅ 의존성 설치
- ✅ Claude Code MCP 설정 자동 추가
- ✅ 기존 MCP 서버 보존 (백업)

### 2. 테스트 (5초)

Claude Code에서:
```
"내가 과거에 Kubernetes 도입할 때 어떤 문제를 겪었어?"
```

## 설정 확인

```bash
# MCP 서버 설정 확인
cat ~/.config/claude/claude_desktop_config.json

# 설정 파일 위치
~/.config/claude/claude_desktop_config.json
```

## 사용 예시

Claude Desktop에서 다음 질문을 해보세요:

```
"내가 과거에 Kubernetes 도입할 때 어떤 문제를 겪었어?"
```

```
"우리 팀 Git 컨벤션이 뭐였지?"
```

```
"데이터베이스 Audit Trail 필드가 뭐였지?"
```

## 고급 테스트

### MCP Inspector 사용

```bash
npx @modelcontextprotocol/inspector ./venv/bin/python run.py
```

브라우저에서 http://localhost:5173 열기.

## 문제가 생겼다면

[TESTING.md](./TESTING.md) 문서의 "문제 해결" 섹션을 참고하세요.
