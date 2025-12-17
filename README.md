# My Tech Blog MCP Server

개인 기술 블로그([jeongil.dev](https://jeongil.dev))의 개발 문서와 경험을 Claude Code에서 직접 조회할 수 있게 해주는 MCP(Model Context Protocol) 서버입니다.

## 왜 만들었나?

### LLM을 나의 개인 아카이브로

이 프로젝트는 단순한 블로그 조회 도구가 아닙니다. **LLM을 나만의 개인 지식 아카이브로 만들기 위한 시도**입니다.

개발하면서 겪은 경험, 내린 결정, 정립한 규칙들을 블로그에 기록해도, 정작 필요할 때 찾아보지 않으면 의미가 없습니다. 같은 실수를 반복하고, 이미 해결했던 문제를 다시 고민하곤 합니다.

MCP 서버를 통해 개발 블로그와 문서를 LLM에 연결하면:
- **과거의 나와 대화할 수 있습니다**: "예전에 Kubernetes 도입할 때 어떤 문제가 있었지?"
- **축적된 지식을 즉시 활용합니다**: "우리 팀 API 설계 원칙이 뭐였지?"
- **같은 실수를 반복하지 않습니다**: "데이터베이스 스키마 설계할 때 꼭 지켜야 할 규칙은?"

### 나만의 Second Brain, LLM과 함께

개발자로서 성장하면서 쌓인 모든 경험과 지식이 한 곳에 아카이빙되고, 언제든 자연어로 질문해서 답을 얻을 수 있습니다.

블로그는 기록의 저장소이고, LLM은 그 기록의 인덱스이자 인터페이스입니다. 내 개발 여정 전체가 하나의 살아있는 지식 베이스가 되는 것입니다.

이것이 이 MCP 서버를 만든 이유입니다.

## 주요 기능

### 📚 Resources (리소스)
- `blog://llms-txt` - 전체 llms.txt 원본 콘텐츠
- `blog://documentation` - 개발 가이드라인 및 컨벤션
- `blog://tech-blog` - 실무 경험 및 기술 블로그 포스트
- `blog://documentation/summary` - 문서 요약
- `blog://tech-blog/summary` - 블로그 포스트 요약

### 🛠️ Tools (도구)
- `search_documentation(query)` - 개발 가이드라인 검색
- `search_experience(query)` - 과거 경험 검색
- `get_category_posts(category)` - 카테고리별 포스트 조회
- `refresh_content()` - 캐시된 콘텐츠 새로고침

### 💬 Prompts (프롬프트 템플릿)
- `check_past_experience` - 과거 유사 문제 해결 경험 조회
- `get_development_guideline` - 특정 개발 가이드라인 조회
- `review_architecture_decision` - 아키텍처 결정 검토

## 설치 방법

### 자동 설치 (권장) ⚡

```bash
# 프로젝트 디렉토리로 이동
cd my-tech-blog-mcp-server
./install.sh
```

**자동으로 처리됩니다:**
- ✅ Python 가상 환경 생성
- ✅ 모든 의존성 설치
- ✅ Claude Code MCP 서버 설정 자동 추가
- ✅ 기존 MCP 서버 설정 보존 (백업 생성)

설치 후 **현재 세션을 종료하고 새 Claude Code 세션을 시작**하면 바로 사용 가능합니다!

**확인 방법:**
```bash
# MCP 서버 등록 확인
claude mcp list

# my-tech-blog 서버가 ✓ Connected로 표시되어야 함
```

### 수동 설치

#### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 2. Claude Code MCP 서버 등록

**방법 1: CLI 명령어 사용 (권장)**
```bash
claude mcp add --transport stdio my-tech-blog -- /path/to/venv/bin/python /path/to/run.py
```

**방법 2: 설정 파일 직접 수정**

설정 파일 위치: `~/.config/claude/claude_desktop_config.json`

다음 내용을 추가:
```json
{
  "mcpServers": {
    "my-tech-blog": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/path/to/run.py"
      ]
    }
  }
}
```

방법 2를 사용한 경우, 추가로 CLI 등록도 필요:
```bash
claude mcp add --transport stdio my-tech-blog -- /path/to/venv/bin/python /path/to/run.py
```

#### 3. 새 세션 시작

현재 Claude Code 세션을 종료하고 새 세션을 시작하면 MCP 서버가 연결됩니다.

## 사용 예시

### 과거 경험 조회
```
"내가 과거에 Kubernetes 도입할 때 어떤 문제를 겪었어?"
```
→ MCP 서버가 Tech Blog에서 관련 경험을 검색하여 제공

### 개발 규칙 확인
```
"우리 팀 Git 컨벤션이 뭐였지?"
```
→ Documentation 섹션에서 Git 워크플로우 및 Conventional Commits 규칙 조회

### 아키텍처 패턴 검토
```
"MSA 전환할 때 어떤 점을 고려했었지?"
```
→ Tech Blog의 Architecture 카테고리에서 관련 경험 조회

## 프로젝트 구조

```
my-tech-blog-mcp-server/
├── src/
│   ├── __init__.py           # 패키지 초기화
│   ├── server.py             # MCP 서버 메인 로직
│   └── llms_parser.py        # llms.txt 파싱 및 검색 로직
├── run.py                    # 서버 실행 진입점
├── pyproject.toml            # 프로젝트 메타데이터 및 의존성
├── requirements.txt          # 의존성 목록
├── claude_desktop_config.json # Claude Code 설정 예제
├── install.sh               # 자동 설치 스크립트
├── check_claude_config.sh   # 설정 확인 스크립트
├── .gitignore               # Git 무시 파일 목록
└── README.md                # 이 문서
```

## 기술 스택

- **Python 3.10+** - 프로그래밍 언어
- **FastMCP** - 2025년 최신 MCP 서버 프레임워크
- **httpx** - 비동기 HTTP 클라이언트
- **Pydantic** - 데이터 검증 및 모델링

## 구현 특징

### 2025년 베스트 프랙티스 적용
1. **FastMCP 사용**: 공식 MCP SDK 기반의 고수준 Pythonic API
2. **자동 스키마 생성**: Docstring과 타입 힌트로 자동 문서화
3. **모듈화된 구조**: Parser와 Server 로직 분리
4. **타입 안정성**: Pydantic 모델을 통한 데이터 검증
5. **캐싱**: llms.txt 콘텐츠 캐싱으로 성능 최적화
6. **비동기 처리**: asyncio 기반 비동기 I/O
7. **간결한 코드**: 데코레이터 패턴으로 50% 이상 코드 감소

### 확장 가능성
- 새로운 Resource 추가 용이
- Tool 함수 확장 가능
- 커스텀 Prompt 템플릿 추가 가능
- 다른 데이터 소스 통합 가능

## 개발

### 로컬 테스트
```bash
python run.py
```

서버가 stdio 모드로 실행되며, MCP 클라이언트(Claude Code)와 통신합니다.

### 코드 포맷팅
```bash
black src/
```

### 린팅
```bash
ruff check src/
```

## 참고 자료

- [Model Context Protocol 공식 문서](https://modelcontextprotocol.io/)
- [FastMCP - Pythonic MCP Framework](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [토스페이먼츠 MCP 서버 구현기](https://toss.tech/article/tosspayments-mcp)
- [jeongil.dev llms.txt](https://jeongil.dev/ko/llms.txt)

## 라이선스

MIT License

## 작성자

@12OneTwo12
