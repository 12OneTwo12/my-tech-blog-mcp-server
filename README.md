# My Tech Blog MCP Server

개인 기술 블로그([jeongil.dev](https://jeongil.dev))의 개발 문서와 경험을 Claude Code에서 직접 조회할 수 있게 해주는 MCP(Model Context Protocol) 서버입니다.

## 왜 만들었나?

### LLM이 내 컨텍스트를 모르면 일반론만 말합니다

Claude Code로 개발하면서 느낀 점이 있습니다. LLM은 똑똑하지만, **나를 모릅니다.**

- "HikariCP Deadlock 어떻게 해결해?" → 일반적인 해결법을 알려줍니다
- "Kubernetes 배포할 때 주의할 점은?" → 범용적인 best practice를 설명합니다
- "Spring Batch 성능 개선 방법은?" → 널리 알려진 튜닝 기법을 나열합니다

틀린 답변은 아닙니다. 하지만 **내가 이미 겪었던 문제, 내가 이미 정리한 규칙, 내가 이미 내린 아키텍처 결정**은 모릅니다.

제 블로그에는 20개가 넘는 트러블슈팅 경험이 있습니다. Kubernetes 도입하면서 겪었던 Pod Graceful Shutdown 문제, JPA와 MyBatis 혼용하면서 만난 HikariCP Deadlock, Spring Batch Chunk 전환 경험 등등. 그리고 팀에서 정립한 Git 컨벤션, API 설계 원칙, 인프라 구성 규칙도 문서화되어 있습니다.

**이 경험들을 LLM이 알고 있다면, 훨씬 더 나에게 맞는 조언을 해줄 수 있다고 생각했습니다.**

### MCP 서버로 블로그를 연결하면 LLM이 나를 이해합니다

그래서 만들었습니다. 블로그를 MCP(Model Context Protocol) 서버로 연결해서, Claude Code가 제 과거 경험과 개발 규칙을 읽을 수 있게 했습니다.

이제는 이렇게 물어볼 수 있습니다:
- "HikariCP Deadlock 문제 또 생겼는데, 예전에 어떻게 해결했었지?"
- "Kubernetes 배포할 때 내가 정리한 주의사항이 뭐였더라?"
- "우리 팀 API 설계 원칙 중에 이 케이스는 어떻게 처리하기로 했지?"

LLM은 제 블로그에서 관련 경험을 찾아서, **내가 과거에 겪었던 구체적인 상황과 해결 방법**을 참고하여 알려줍니다. 일반론이 아닌, 나의 컨텍스트를 기반으로 한 답변을 줍니다.

**블로그는 나의 경험이 쌓이는 저장소, LLM은 그 경험을 이해하고 활용하는 Second Brain이 될수 있을 거라 생각합니다.**

같은 실수를 반복하지 않고, 과거의 내가 쌓아둔 지식을 현재 개발에 즉시 활용하며, 일관된 개발 규칙을 유지할 수 있게 만드는 것. 그것이 이 MCP 서버를 만든 이유입니다.

<img width="701" height="849" alt="image" src="https://github.com/user-attachments/assets/59e4a407-d4a0-40ea-ae57-7eaeaccb37e8" />

## 주요 기능

### 📚 Resources (리소스)
- `blog://llms-txt` - 전체 llms.txt 원본 콘텐츠
- `blog://documentation` - 개발 가이드라인 및 컨벤션
- `blog://tech-blog` - 실무 경험 및 기술 블로그 포스트
- `blog://documentation/summary` - 문서 요약
- `blog://tech-blog/summary` - 블로그 포스트 요약 (메타데이터 포함)

### 🛠️ Tools (도구)

#### 🔍 검색 도구 (BM25 Ranking)
- `search_all(query, top_k=10)` - **전체 컨텐츠 통합 검색** (가장 강력한 검색)
- `search_documentation(query, top_k=10)` - 개발 가이드라인 검색
- `search_experience(query, top_k=10)` - 과거 경험 검색
- `get_category_posts(category)` - 카테고리별 포스트 조회

#### 📅 시간 기반 도구
- `get_recent_posts(days=30, category=None)` - 최근 N일간 포스트 조회

#### ⚙️ 관리 도구
- `refresh_content()` - 캐시된 콘텐츠 새로고침
- `health_check()` - 서버 상태 확인

### 💬 Prompts (프롬프트 템플릿)
- `check_past_experience` - 과거 유사 문제 해결 경험 조회
- `get_development_guideline` - 특정 개발 가이드라인 조회
- `review_architecture_decision` - 아키텍처 결정 검토

### ✨ 2025 베스트 프랙티스 개선 사항

#### 🚀 BM25 시맨틱 검색
- **기존**: 단순 substring 검색
- **개선**: BM25 알고리즘 기반 관련도 점수 랭킹
- **효과**: 검색 품질 대폭 향상, 한글/영어 모두 지원

#### 🔄 TTL 기반 캐싱
- **기존**: 메모리 캐시만 존재, 만료 없음
- **개선**: 설정 가능한 TTL (기본 60분)
- **효과**: 최신 콘텐츠 자동 갱신, 메모리 효율성

#### 🛡️ 회복 탄력적 HTTP 클라이언트
- **기존**: 에러 시 즉시 실패
- **개선**: 재시도 로직 + 지수 백오프 + Circuit Breaker
- **효과**: 네트워크 장애 복원력 향상

#### 📊 풍부한 메타데이터
- **기존**: 제목과 내용만 파싱
- **개선**: 발행일, URL, 카테고리, 태그 자동 추출
- **효과**: 시간 기반 필터링, 정확한 분류

#### ⚙️ 환경 변수 설정
- **기존**: 하드코딩된 URL
- **개선**: 모든 설정을 환경 변수로 제어 가능
- **효과**: 다른 블로그/환경에도 쉽게 적용

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

### 환경 변수 설정 (선택사항)

`.env` 파일을 생성하여 설정을 커스터마이징할 수 있습니다:

```bash
cp .env.example .env
```

**사용 가능한 환경 변수:**

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BLOG_BASE_URL` | `https://jeongil.dev` | 블로그 기본 URL |
| `BLOG_LLMS_PATH` | `/ko/llms.txt` | llms.txt 경로 |
| `BLOG_CACHE_TTL_MINUTES` | `60` | 캐시 유효 시간 (분) |
| `BLOG_HTTP_TIMEOUT` | `30.0` | HTTP 요청 타임아웃 (초) |
| `BLOG_HTTP_MAX_RETRIES` | `3` | HTTP 재시도 최대 횟수 |
| `BLOG_HTTP_RETRY_DELAY` | `1.0` | 재시도 지연 시간 (초) |

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
2. **BM25 검색 엔진**: 순수 Python 구현, 외부 의존성 없음
3. **자동 스키마 생성**: Docstring과 타입 힌트로 자동 문서화
4. **모듈화된 구조**: Parser와 Server 로직 분리
5. **타입 안정성**: Pydantic 모델을 통한 데이터 검증
6. **TTL 캐싱**: 자동 만료 및 갱신으로 메모리 효율성 확보
7. **회복 탄력성**: 재시도 + Circuit Breaker로 안정성 확보
8. **비동기 처리**: asyncio 기반 비동기 I/O
9. **환경 변수**: 모든 설정을 외부화하여 유연성 확보
10. **간결한 코드**: 데코레이터 패턴으로 50% 이상 코드 감소

### 확장 가능성
- 새로운 Resource 추가 용이
- Tool 함수 확장 가능
- 커스텀 Prompt 템플릿 추가 가능
- 다른 데이터 소스 통합 가능 (환경 변수로 URL만 변경)
- BM25 파라미터 튜닝 가능

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
