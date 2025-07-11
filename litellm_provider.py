import sys
import json
from litellm import completion
import time
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

# 로깅 설정
log_file_path = Path(__file__).parent / 'debug.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stderr)
    ]
)

def load_environment_variables():
    """환경 변수를 로드하고 설정을 확인합니다."""
    # .env 파일에서 환경 변수 로드
    load_dotenv()
    
    # 로드된 환경 변수 확인
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'COHERE_API_KEY': os.getenv('COHERE_API_KEY')
    }
    
    logging.info("환경 변수 로드 완료:")
    for key, value in env_vars.items():
        if value:
            logging.info(f"  {key}: {'*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '***'}")
        else:
            logging.warning(f"  {key}: 설정되지 않음")
    
    return env_vars

def get_model_config(model_name, env_vars):
    """모델별 설정을 반환합니다."""
    model_lower = model_name.lower()
    
    # 명시적 provider가 지정된 경우 (예: openrouter:gpt-4, litellm:gpt-3.5-turbo, ollama:gemma3:12b)
    if ':' in model_name:
        provider, actual_model = model_name.split(':', 1)
        provider_lower = provider.lower()
        
        if provider_lower == 'openrouter':
            if not env_vars['OPENROUTER_API_KEY']:
                raise ValueError("OPENROUTER_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
            return {
                'api_base': 'https://openrouter.ai/api/v1',
                'api_key': env_vars['OPENROUTER_API_KEY'],
                'provider': 'openrouter',
                'model': actual_model
            }
        elif provider_lower == 'litellm':
            return {
                'api_base': 'http://localhost:8000/v1',
                'api_key': 'not-needed',
                'provider': 'litellm',
                'model': actual_model
            }
        elif provider_lower == 'ollama':
            # direct REST API 연결
            api_base = os.getenv('OLLAMA_API_BASE', 'http://localhost:11434')
            return {
                'api_base': api_base,
                'api_key': 'not-needed',
                'provider': 'ollama',
                'model': actual_model,
                'direct': True
            }
        else:
            # 알 수 없는 provider는 기본 모델 매핑 사용
            return get_default_model_config(actual_model, env_vars)
    
    # 기본 모델 매핑 (provider가 명시되지 않은 경우)
    return get_default_model_config(model_name, env_vars)

def get_default_model_config(model_name, env_vars):
    """기본 모델별 설정을 반환합니다."""
    model_lower = model_name.lower()
    
    # OpenAI 모델들 (gpt-3.5-turbo, gpt-4, gpt-4o 등)
    if any(prefix in model_lower for prefix in ['gpt-', 'dall-e', 'whisper', 'text-embedding']):
        if not env_vars['OPENAI_API_KEY']:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return {
            'api_base': None,  # OpenAI 기본 URL 사용
            'api_key': env_vars['OPENAI_API_KEY'],
            'provider': 'openai'
        }
    
    # Google/Gemini 모델들
    elif any(prefix in model_lower for prefix in ['gemini', 'palm', 'text-bison']):
        if not env_vars['GOOGLE_API_KEY']:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return {
            'api_base': None,  # Google 기본 URL 사용
            'api_key': env_vars['GOOGLE_API_KEY'],
            'provider': 'google'
        }
    
    # Perplexity 모델들
    elif any(prefix in model_lower for prefix in ['sonar', 'llama', 'mistral', 'codellama']):
        if not env_vars['PERPLEXITY_API_KEY']:
            raise ValueError("PERPLEXITY_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        # Perplexity 모델명 정규화
        if 'sonar' in model_lower:
            normalized_model = 'perplexity/sonar'
        else:
            normalized_model = f'perplexity/{model_name}'
        return {
            'api_base': None,  # Perplexity 기본 URL 사용
            'api_key': env_vars['PERPLEXITY_API_KEY'],
            'provider': 'perplexity',
            'model': normalized_model
        }
    
    # Anthropic 모델들 (claude-3, claude-2 등)
    elif any(prefix in model_lower for prefix in ['claude']):
        if not env_vars.get('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return {
            'api_base': None,  # Anthropic 기본 URL 사용
            'api_key': env_vars['ANTHROPIC_API_KEY'],
            'provider': 'anthropic'
        }
    
    # Cohere 모델들
    elif any(prefix in model_lower for prefix in ['command', 'embed']):
        if not env_vars.get('COHERE_API_KEY'):
            raise ValueError("COHERE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return {
            'api_base': None,  # Cohere 기본 URL 사용
            'api_key': env_vars['COHERE_API_KEY'],
            'provider': 'cohere'
        }
    
    # 기본값: LiteLLM 서버 사용 (알 수 없는 모델)
    else:
        logging.warning(f"알 수 없는 모델 '{model_name}'을 LiteLLM 서버로 라우팅합니다.")
        return {
            'api_base': 'http://localhost:8000/v1',
            'api_key': 'not-needed',
            'provider': 'litellm'
        }

def main():
    try:
        logging.info("=== 스크립트 시작 ===")
        
        # 1. 환경 변수 로드
        env_vars = load_environment_variables()
        
        # 2. stdin에서 JSON 읽기
        stdin_content = sys.stdin.read().strip()
        if not stdin_content:
            raise ValueError("stdin이 비어있습니다")
        
        logging.info("stdin 데이터 수신 완료")
        logging.debug(f"stdin 데이터: {stdin_content}")
        
        # 3. JSON 파싱
        try:
            data = json.loads(stdin_content)
            logging.info("JSON 파싱 성공")
            logging.debug(f"파싱된 데이터: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON 파싱 실패: {e}")
            raise
            
        # 4. 필수 필드 추출
        prompt = data.get("prompt")
        vars_data = data.get("vars", {})
        
        # query가 있으면 prompt로 사용 (promptfoo에서 query 변수를 사용하는 경우)
        if not prompt and vars_data.get("query"):
            prompt = vars_data["query"]
        
        # 모델명 결정 (vars에서 model이 있으면 사용, 없으면 기본값)
        model = vars_data.get("model", os.getenv("LITELLM_MODEL", "gpt-3.5-turbo"))
        temperature = float(vars_data.get("temperature", 0.7))
        
        if not prompt:
            raise ValueError("prompt가 비어있습니다")
        
        # 5. 모델별 설정 가져오기
        model_config = get_model_config(model, env_vars)
        
        logging.info(f"모델: {model}")
        logging.info(f"Provider: {model_config['provider']}")
        logging.info(f"API Base: {model_config['api_base']}")
        logging.info(f"Temperature: {temperature}")
        logging.debug(f"Prompt: {prompt[:100]}...")
        
        # Ollama direct 처리
        if model_config.get('provider') == 'ollama' and model_config.get('direct'):
            import requests
            payload = {
                "model": model_config['model'],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            response = requests.post(
                f"{model_config['api_base']}/api/chat",
                json=payload
            )
            if response.status_code == 200:
                result = {"text": response.json()['message']['content']}
                print(json.dumps(result))
                logging.info("=== 정상 종료 (Ollama direct) ===")
                return
            else:
                raise RuntimeError(f"Ollama direct API 오류: {response.text}")
        
        # 나머지 모델은 litellm completion 사용
        completion_kwargs = {
            "model": model_config.get('model', model),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        # API 키와 base가 설정된 경우에만 추가
        if model_config['api_key'] and model_config['api_key'] != 'not-needed':
            completion_kwargs["api_key"] = model_config['api_key']
        
        if model_config['api_base']:
            completion_kwargs["api_base"] = model_config['api_base']
        
        # 7. API 호출
        response = completion(**completion_kwargs)
        
        # 8. 결과 반환
        result = {
            "text": response.choices[0].message.content
        }
        
        print(json.dumps(result))
        logging.info("=== 정상 종료 ===")
        
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}", exc_info=True)
        error_result = {
            "error": str(e)
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 