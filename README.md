# LLM 모델 및 프롬프트 평가 플랫폼

이 프로젝트는 `promptfoo`와 `litellm`을 사용하여 다양한 LLM(대규모 언어 모델)의 성능과 다양한 프롬프트 조합을 체계적으로 테스트하고 평가하기 위한 플랫폼입니다.

## 주요 기술

- **[promptfoo](https://www.promptfoo.dev/):** LLM 앱을 위한 테스트 프레임워크. 프롬프트, 모델, 품질 평가를 자동화합니다.
- **[litellm](https://www.litellm.ai/):** 100개 이상의 LLM API를 OpenAI 표준 형식으로 호출할 수 있게 해주는 라이브러리입니다.

## 시스템 아키텍처

```
PromptFoo → custom-litellm-provider.js → litellm_provider.py → LiteLLM → API
```

### 핵심 구성요소
1. **promptfooconfig.yaml**: 테스트 정의 및 평가 설정
2. **custom-litellm-provider.js**: PromptFoo JavaScript 커스텀 provider
3. **litellm_provider.py**: 다중 LLM API 통합 Python 스크립트
4. **.env**: API 키 및 환경변수 설정

## 시작하기

### 1. 사전 준비

- [Node.js](https://nodejs.org/) (v18 이상) 및 npm
- Python (v3.10 이상)
- 필요한 LLM API 키들

### 2. 프로젝트 설정

```bash
# 1. 의존성 설치
pip install -r requirements.txt
npm install -g promptfoo

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 API 키 입력
```

### 3. 환경변수 설정 (.env 파일)

```bash
# 필수 API 키들
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
PERPLEXITY_API_KEY=pplx-...

# 선택적 API 키들  
OPENROUTER_API_KEY=sk-or-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...

# Ollama 설정 (로컬 사용시)
OLLAMA_API_BASE=http://localhost:11434
```

### 4. 평가 실행

```bash
# 전체 평가 실행
npx promptfoo eval --config promptfooconfig.yaml

# 첫 번째 테스트만 실행 (빠른 테스트)
npx promptfoo eval --config promptfooconfig.yaml --filter-first-n 1

# 특정 모델만 테스트
npx promptfoo eval --config promptfooconfig.yaml --filter-providers "gpt-3.5-turbo"

# 웹 UI로 결과 확인
npx promptfoo view
```

## 🚀 **대표 실험 방식 및 예시**

### 📊 **실험 방식 1: CSV 기반 정밀 조합** 
> 🎯 **목적**: 엑셀/구글시트처럼 직관적인 조합 관리  
> 📁 **설정 파일**: `youtube_summary.yaml` + `tests/test.csv`

**✨ 사용 예시**:
```bash
# 1. CSV 파일 편집
vim tests/test.csv

# 2. 실행
npx promptfoo eval -c youtube_summary.yaml
```

**📝 CSV 템플릿** (`tests/test.csv`):
```csv
query,temperature,model,provider,prompt
"AI 에이전트 최신 연구",0.7,gpt-3.5-turbo,openai,summary_prompt
"멀티모달 LLM 동향",0.5,gemini-1.5-flash,google,twitter_style_prompt
"RAG 시스템 설계 패턴",0.3,sonar,perplexity,academic_style_prompt
"Test Time Compute",0.8,gemma3:12b,ollama,summary_prompt
```

**🔥 장점**: 
- ✅ 정확한 조합 제어 (행별로 독립적)
- ✅ 비개발자도 쉽게 수정 가능
- ✅ 빠른 A/B 테스트

---

### 🔬 **실험 방식 2: YAML 자동 조합 매트릭스**
> 🎯 **목적**: 프롬프트×모델 전체 조합 자동 생성  
> 📁 **설정 파일**: `promptfooconfig.yaml`

**✨ 사용 예시**:
```bash
# 복합 실험 실행 (3 프롬프트 × 4 모델 = 12가지 조합)
npx promptfoo eval -c promptfooconfig.yaml

# 빠른 개발 테스트 (첫 번째만)
npx promptfoo eval -c promptfooconfig.yaml --filter-first-n 1
```

**📝 설정 예시**:
```yaml
tests:
  - description: "📈 프롬프트 스타일별 요약 품질 매트릭스"
    prompts:
      - "prompts/basic.txt"              # 기본 스타일
      - "prompts/summary/academic_style_prompt.txt"  # 학술 스타일  
      - "prompts/summary/twitter_style_prompt.txt"   # 소셜미디어 스타일
    providers:
      - config: {model: gpt-3.5-turbo}    # OpenAI
      - config: {model: gemini-flash}     # Google
      - config: {model: perplexity-sonar} # Perplexity
      - config: {model: ollama/gemma3:12b} # Local
    vars:
      query: file://queries/summary_query.txt
    # 🔄 결과: 3×4 = 12가지 조합 자동 생성
```

**🔥 장점**:
- ✅ 대규모 비교 실험
- ✅ 체계적 성능 벤치마크
- ✅ 통계적 유의성 확보

---

### ⚡ **실험 방식 3: 간편 프로토타이핑** 
> 🎯 **목적**: 빠른 아이디어 검증 및 개발  
> 📁 **설정 파일**: `test.yaml`

**✨ 사용 예시**:
```bash
# 간단한 2×3 조합 테스트
npx promptfoo eval -c test.yaml
```

**📝 설정 예시**:
```yaml
description: "💡 빠른 프롬프트 비교"
prompts:
  - file://prompts/summary_prompt.txt    # 일반 요약
  - file://prompts/twitter_style_prompt.txt  # 트위터 스타일

providers:
  - id: "google:gemini-1.5-flash"
  - id: "perplexity:sonar" 
  - id: "ollama:gemma3"

defaultTest:
  vars:
    query: "Test Time Compute, Reasoning, LLM Agents 최신 연구"
    temperature: 0.7
```

**🔥 장점**:
- ✅ 30초 내 실험 시작
- ✅ 아이디어 빠른 검증
- ✅ 리소스 효율적

---

### 🎬 **실험 방식 4: 도메인 특화 테스트**
> 🎯 **목적**: 유튜브 영상, 논문 등 특정 도메인 최적화  
> 📁 **설정 파일**: `youtube_summary.yaml`

**✨ 사용 예시**:
```bash
# 유튜브 영상 요약 프롬프트 비교
npx promptfoo eval -c youtube_summary.yaml
```

**📝 설정 예시**:
```yaml
description: "📺 유튜브 요약 프롬프트 최적화"
prompts:
  - file://prompts/summary/v09.txt      # 간결형
  - file://prompts/summary/v111.txt     # 상세형
  - file://prompts/summary/v2.txt       # 구조화형

defaultTest:
  vars:
    video_input:
      file_data:
        file_uri: "https://youtu.be/Lv3QwcAcDnA"
        mime_type: "video/*"
    query: "이 비디오의 주요 내용을 요약해줘"
```

**🔥 장점**:
- ✅ 도메인별 최적화
- ✅ 실제 사용 케이스 반영
- ✅ 전문 평가 기준

---

## 🛠️ **실험 실행 명령어 모음**

### **개발/테스트 단계**
```bash
# 🚀 빠른 프로토타입 (2×3=6가지)
npx promptfoo eval -c test.yaml

# 🧪 첫 번째 조합만 테스트
npx promptfoo eval -c test.yaml --filter-first-n 1

# 📊 특정 모델만 테스트
npx promptfoo eval --filter-providers "gemini"
```

### **정밀 실험 단계**  
```bash
# 📈 정밀 조합 실험 (CSV 기반)
npx promptfoo eval -c youtube_summary.yaml

# 🔬 전체 매트릭스 실험 (3×4=12가지)
npx promptfoo eval -c promptfooconfig.yaml

# 📋 결과 웹 UI로 확인
npx promptfoo view
```

### **프로덕션 검증**
```bash
# 🎯 도메인 특화 테스트
npx promptfoo eval -c youtube_summary.yaml

# 📊 성능 벤치마크 (상세 로그)
npx promptfoo eval -c promptfooconfig.yaml --verbose

# 💾 결과 CSV 저장
npx promptfoo eval -c test.yaml --output ./results/
```

## 지원 모델

### 현재 설정된 모델들
- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4o 등
- **Google**: gemini-flash, gemini-pro 등
- **Perplexity**: perplexity-sonar 등
- **Ollama**: ollama/gemma3:12b 등 (로컬 설치 필요)

### 모델 추가하기

1. **litellm_provider.py**에서 모델 매핑 확인
2. **promptfooconfig.yaml**에서 provider 설정 추가
3. 해당 API 키를 **.env**에 추가

## 프롬프트 및 테스트 구성

### 프롬프트 파일들
- `prompts/basic.txt`: 기본 설명 프롬프트
- `prompts/summary/`: 다양한 스타일의 요약 프롬프트들
- `prompts/analysis.txt`: 분석 전용 프롬프트

### 쿼리 파일들
- `queries/summary_query.txt`: 요약 관련 질문
- `queries/analysis_query.txt`: 분석 관련 질문

### 평가 방식
- **LLM Rubric 평가**: GPT-4o를 평가자로 사용한 자동 품질 평가
- **평가 기준**: `prompts/single_evaluation_rubric.txt`에 정의

## 설정 파일 상세

### promptfooconfig.yaml 구조

```yaml
providers:
  - id: file://./custom-litellm-provider.js

tests:
  - description: "프롬프트 스타일에 따른 요약 품질 비교"
    prompts:
      - "prompts/basic.txt"
      - "prompts/summary/summary_prompt.txt"
    vars:
      query: file://queries/summary_query.txt
    providers:
      - id: file://./custom-litellm-provider.js
        config:
          model: gpt-3.5-turbo
    assert:
      - type: llm-rubric
        value: file://prompts/single_evaluation_rubric.txt
        provider: file://./custom-litellm-provider.js
        config:
          model: gpt-4o
```

## 문제 해결

### 일반적인 오류들

1. **"prompt가 비어있습니다"**
   - 원인: 템플릿 변수 처리 오류
   - 해결: `{{query}}` 변수가 올바르게 설정되었는지 확인

2. **API 키 오류**
   - 원인: .env 파일의 API 키 문제
   - 해결: API 키 유효성 확인 및 올바른 형식 확인

3. **모델 인식 오류**
   - 원인: 지원하지 않는 모델명 또는 API 키 부족
   - 해결: 모델명 확인 및 해당 API 키 설정

### 디버그 모드

```bash
# Python 스크립트 로그 확인
tail -f debug.log

# 상세 에러 로그
npx promptfoo eval --config promptfooconfig.yaml --verbose
```

## 확장 및 커스터마이징

### 새로운 평가 메트릭 추가
1. `prompts/` 디렉토리에 새 rubric 파일 생성
2. `promptfooconfig.yaml`의 assert 섹션에 추가

### 새로운 프롬프트 스타일 추가
1. `prompts/` 디렉토리에 새 프롬프트 파일 생성
2. `promptfooconfig.yaml`의 prompts 리스트에 추가

### 배치 처리 및 성능 최적화
- `--max-concurrency` 옵션으로 동시 실행 수 조절
- `--repeat` 옵션으로 반복 테스트 설정

## 참고 자료

- [PromptFoo 공식 문서](https://promptfoo.dev/docs/)
- [LiteLLM 공식 문서](https://docs.litellm.ai/)
- [지원하는 LLM 목록](https://docs.litellm.ai/docs/providers)

## 프로젝트 구조

```
llm_promptfoo/
├── promptfooconfig.yaml      # 메인 설정 파일
├── custom-litellm-provider.js # PromptFoo JavaScript provider
├── litellm_provider.py       # Python LLM 통합 스크립트
├── .env                      # 환경변수 (API 키들)
├── prompts/                  # 프롬프트 템플릿들
│   ├── basic.txt
│   ├── analysis.txt
│   ├── evaluation_rubric.txt
│   └── summary/
├── queries/                  # 테스트 쿼리들
├── tests/                    # 테스트 데이터
└── README.md                # 이 파일
```