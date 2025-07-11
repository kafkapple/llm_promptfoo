// custom-litellm-provider.js
const { execSync } = require('child_process');

class CustomLiteLLMProvider {
  constructor(options) {
    this.providerId = options.id || 'custom-litellm-provider';
    this.config = options.config || {};
    this.apiBase = this.config.apiBase || 'http://localhost:8000/v1';
  }

  id() {
    return this.providerId;
  }

  async callApi(prompt, context) {
    const model = this.config.model || (context && context.vars ? context.vars.model : null) || 'gpt-3.5-turbo';
    
    // {{query}} 템플릿 처리
    let finalPrompt = prompt;
    if (context && context.vars && context.vars.query) {
      finalPrompt = prompt.replace(/\{\{query\}\}/g, context.vars.query);
    }
    
    const payload = {
      prompt: finalPrompt,
      vars: {
        model: model,
        temperature: this.config.temperature || 0.7,
        ...(context && context.vars ? context.vars : {})
      }
    };

    try {
      const input = JSON.stringify(payload);
      const result = execSync('python litellm_provider.py', {
        input: input,
        encoding: 'utf8',
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      });

      const response = JSON.parse(result);
      
      if (response.error) {
        throw new Error(response.error);
      }

      return {
        output: response.text,
        tokenUsage: {
          total: 0,
          prompt: 0,
          completion: 0,
        },
      };
    } catch (error) {
      console.error('Error calling Python provider:', error);
      throw error;
    }
  }
}

module.exports = CustomLiteLLMProvider;
