# MCP 서버 테스트 가이드

MCP 서버가 제대로 작동하는지 테스트하는 방법입니다.

## 방법 1: 로컬 유닛 테스트 (빠른 검증) ✅

서버의 핵심 기능이 작동하는지 빠르게 확인합니다.

```bash
./venv/bin/python test_mcp_server.py
```

**테스트 항목:**
- ✅ llms.txt 파싱 (8,104자, 9개 섹션)
- ✅ Documentation 검색
- ✅ Tech Blog 검색

**결과:**
```
✓ Successfully fetched content (8104 chars)
✓ Documentation sections: 2
✓ Tech Blog sections: 7
✓ Search returned 2 results
```

## 방법 2: MCP Inspector (권장) 🔍

공식 MCP Inspector를 사용하면 실제 MCP 프로토콜을 통해 서버를 테스트할 수 있습니다.

### 설치 및 실행

```bash
# MCP Inspector 실행
npx @modelcontextprotocol/inspector ./venv/bin/python run.py
```

**Inspector에서 테스트 가능한 항목:**
1. **Resources 조회**
   - `blog://llms-txt` 전체 콘텐츠
   - `blog://documentation` 개발 가이드라인
   - `blog://tech-blog` 기술 블로그

2. **Tools 실행**
   - `search_documentation(query="git")`
   - `search_experience(query="kubernetes")`
   - `get_category_posts(category="backend")`
   - `refresh_content()`

3. **Prompts 사용**
   - `check_past_experience(topic="...")`
   - `get_development_guideline(guideline_type="...")`
   - `review_architecture_decision(architecture_topic="...")`

### Inspector 사용법

1. 브라우저에서 Inspector UI가 열립니다 (보통 http://localhost:5173)
2. 왼쪽에서 Resources/Tools/Prompts 탭 선택
3. 각 항목을 클릭하여 실행
4. 오른쪽에서 결과 확인

## 방법 3: Claude Desktop 연결 (실제 환경) 🚀

실제 Claude Desktop에서 사용하는 것과 동일한 환경으로 테스트합니다.

### 1단계: Claude Desktop 설정

Claude Desktop 설정 파일 열기:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

다음 내용 추가:
```json
{
  "mcpServers": {
    "my-tech-blog": {
      "command": "/Users/jeongjeong-il/Desktop/projects/my-tech-blog-mcp-server/venv/bin/python",
      "args": [
        "/Users/jeongjeong-il/Desktop/projects/my-tech-blog-mcp-server/run.py"
      ]
    }
  }
}
```

### 2단계: Claude Desktop 재시작

완전히 종료하고 다시 시작합니다.

### 3단계: 서버 활성화 확인

Claude Desktop 하단에 "my-tech-blog" MCP 서버가 연결되었다는 표시가 나타납니다.

### 4단계: 테스트 질문

Claude에게 다음과 같이 질문해보세요:

```
"내가 과거에 Kubernetes 도입할 때 어떤 문제를 겪었어?"
```

```
"우리 팀 Git 컨벤션이 뭐였지?"
```

```
"데이터베이스 설계할 때 꼭 지켜야 할 규칙 알려줘"
```

## 방법 4: 직접 서버 실행 (디버깅용)

서버를 직접 실행하고 로그를 확인합니다.

```bash
./venv/bin/python run.py
```

**예상 출력:**
```
INFO:server:Starting My Tech Blog MCP Server...
INFO:server:Serving content from: https://jeongil.dev/ko/llms.txt
INFO:mcp.server:Server running on stdio transport
```

서버가 실행되면 stdio 모드로 대기합니다. 이 상태에서 Claude Desktop이나 MCP Inspector가 연결할 수 있습니다.

종료하려면 `Ctrl+C`를 누르세요.

## 문제 해결

### 서버가 시작되지 않음

```bash
# 의존성 재설치
./install.sh
```

### llms.txt를 가져올 수 없음

```bash
# 네트워크 연결 확인
curl https://jeongil.dev/ko/llms.txt

# httpx가 제대로 설치되었는지 확인
./venv/bin/python -c "import httpx; print(httpx.__version__)"
```

### Claude Desktop에서 서버가 보이지 않음

1. 설정 파일 확인 (경로에 공백이 있으므로 따옴표 필수):
   ```bash
   # macOS
   cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

   # 또는 백슬래시 escape
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. JSON 문법 오류 확인 (쉼표, 중괄호 등)

3. Claude Desktop 완전 재시작 (Task Manager/Activity Monitor에서 종료)

4. 로그 확인:
   ```bash
   # macOS
   ls -la "$HOME/Library/Logs/Claude/"

   # Windows (PowerShell)
   dir "$env:APPDATA\Claude\logs\"
   ```

### MCP Inspector 실행 오류

```bash
# Node.js가 설치되어 있는지 확인
node --version

# 없으면 설치
brew install node  # macOS
```

## 테스트 체크리스트

- [ ] 로컬 유닛 테스트 통과 (`test_mcp_server.py`)
- [ ] llms.txt 파싱 성공 (`test_connection.py`)
- [ ] MCP Inspector로 Resources 조회 가능
- [ ] MCP Inspector로 Tools 실행 가능
- [ ] MCP Inspector로 Prompts 사용 가능
- [ ] Claude Desktop 설정 완료
- [ ] Claude Desktop에서 질문에 답변 받기

## 성공 기준

✅ **핵심 기능 테스트 통과**
- llms.txt에서 8,104자 콘텐츠 가져오기
- Documentation 2개 섹션 파싱
- Tech Blog 7개 섹션 파싱
- 검색 기능 작동

✅ **MCP Inspector 테스트**
- 모든 Resources 조회 가능
- 모든 Tools 실행 가능
- 모든 Prompts 사용 가능

✅ **Claude Desktop 연동**
- 서버 연결 표시 확인
- 실제 질문에 대한 답변 받기
- 과거 경험 조회 성공
- 개발 규칙 조회 성공

모든 테스트가 통과하면 MCP 서버가 정상적으로 작동하는 것입니다! 🎉
