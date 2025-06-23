# LLM 모델 및 프롬프트 평가 플랫폼

이 프로젝트는 `promptfoo`와 `litellm`을 사용하여 다양한 LLM(대규모 언어 모델)의 성능과 다양한 프롬프트 조합을 체계적으로 테스트하고 평가하기 위한 플랫폼입니다.

모든 설정은 `promptfooconfig.yaml` 파일 하나로 관리되어 간결하고 확장 가능합니다.

## 주요 기술

*   **[promptfoo](https://www.promptfoo.dev/):** LLM 앱을 위한 테스트 프레임워크. 프롬프트, 모델, 품질 평가를 자동화합니다.
*   **[litellm](https://www.litellm.ai/):** 100개 이상의 LLM API를 OpenAI 표준 형식으로 호출할 수 있게 해주는 라이브러리입니다.

## 현재 API 사용 방식

### 1. LiteLLM 서버 (포트 8000)
- **설정 파일**: `litellm.config.yaml`
- **실행 명령**: `litellm --config litellm.config.yaml --port 8000`
- **지원 모델**:
  - `gemini-flash`: Google Gemini 1.5 Pro (Google API)
  - `openrouter-gemini`: OpenRouter를 통한 Gemini 1.5 Pro
  - `gemma`: Ollama Gemma 모델 연동

### 2. Ollama 서버 (포트 11434)
- **실행 명령**: `ollama serve`
- **사용 가능한 모델**: `ollama list`로 확인
- **주요 모델**: gemma3:12b, llama2:latest, gemma:latest 등

### 3. Promptfoo 설정
- **설정 파일**: `promptfooconfig.yaml`
- **프롬프트 파일**:
  - `prompts/summary_prompt.txt`: 구조화된 요약
  - `prompts/twitter_style_prompt.txt`: 트위터 스타일 설명
- **Provider 설정**:
  - LiteLLM: `http://localhost:8000/v1`
  - Ollama: `http://localhost:11434/v1`

## 시작하기

### 1. 사전 준비

*   [Node.js](https://nodejs.org/) (v18 이상) 및 npm이 설치되어 있어야 합니다.
*   Python (v3.10 이상)이 설치되어 있어야 합니다.
*   [Ollama](https://ollama.ai/)가 설치되어 있어야 합니다.

### 2. 프로젝트 클론 및 설정

```bash
# 1. 프로젝트를 클론합니다.
git clone <repository-url>
cd <repository-name>

# 2. 필요한 파이썬 패키지를 설치합니다.
pip install -r requirements.txt

# 3. promptfoo를 설치합니다.
npm install -g promptfoo

# 4. .env 파일을 생성하고 LLM API 키를 입력합니다.
# (예시: GOOGLE_API_KEY, OPENROUTER_API_KEY 등)
```

### 3. `.env` 파일 예시

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```
# API Keys
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Server Settings
LITELLM_PORT=8000
OLLAMA_PORT=11434
```

### 4. 서버 실행

```bash
# 1. Ollama 서버 실행 (백그라운드)
ollama serve

# 2. LiteLLM 서버 실행 (백그라운드)
litellm --config litellm.config.yaml --port 8000
```

### 5. 평가 실행

```bash
# 평가 실행
promptfoo eval

# 결과 확인 (웹 UI)
promptfoo view
```

## 설정 파일 상세

### `litellm.config.yaml`
```yaml
model_list:
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-1.5-pro
      api_key: ${GOOGLE_API_KEY}
      api_base: https://generativelanguage.googleapis.com/v1beta/models

  - model_name: openrouter-gemini
    litellm_params:
      model: openrouter/google/gemini-1.5-pro
      api_key: ${OPENROUTER_API_KEY}
      api_base: https://openrouter.ai/api/v1

  - model_name: gemma
    litellm_params:
      model: ollama/gemma
      api_base: http://localhost:11434/v1

general_settings:
  default_model: gemini-flash
```

### `promptfooconfig.yaml`
- `prompts`: 테스트할 프롬프트 템플릿 목록
- `providers`: LLM 호출 방법 정의 (LiteLLM, Ollama)
- `tests`: 실제 테스트 시나리오 (단계별 평가 기준)

## 테스트 단계

1. **레벨 1 (기본)**: 키워드 포함 여부, 최소 길이 체크
2. **레벨 2 (구조)**: 구조화된 응답, 6점 만점에 4점 이상
3. **레벨 3 (전문성)**: 전문 용어, 구체적 사례, 6점 만점에 4점 이상
4. **레벨 4 (창의성)**: 트위터 스타일, 이모지 사용, 6점 만점에 3점 이상

## 문제 해결

### 포트 충돌
```bash
# 실행 중인 프로세스 확인
netstat -ano | findstr "8000 11434"

# 프로세스 종료
taskkill /F /PID <process_id>
```

### 프롬프트 파일 적용 안됨
- `promptfooconfig.yaml`의 테스트 케이스에 `prompt: "summary"` 또는 `prompt: "twitter"` 추가 필요
