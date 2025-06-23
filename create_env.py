# .env 파일 생성
env_content = """# API Keys for LLM providers
# 실제 API 키로 교체하세요

OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
PERPLEXITY_API_KEY=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
OPENROUTER_API_KEY=your_openrouter_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print(".env 파일이 생성되었습니다.")
print("Perplexity API 키가 추가되었습니다.")
print("다른 API 키들은 별도로 설정해야 합니다.") 