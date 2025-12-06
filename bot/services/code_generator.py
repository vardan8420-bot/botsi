"""
AI Разработчик - генерация и анализ кода
"""
from typing import Optional, Dict, List
from openai import OpenAI


class CodeGenerator:
    """Генератор кода через OpenAI"""
    
    def __init__(self, api_key: str):
        """
        Инициализация генератора
        
        Args:
            api_key: OpenAI API ключ
        """
        self.client = OpenAI(api_key=api_key)
    
    async def generate_code(
        self,
        description: str,
        language: str = 'python',
        framework: str = None
    ) -> Optional[str]:
        """
        Генерация кода по описанию
        
        Args:
            description: Описание что нужно создать
            language: Язык программирования
            framework: Фреймворк (опционально)
            
        Returns:
            Сгенерированный код
        """
        try:
            framework_text = f" using {framework}" if framework else ""
            
            prompt = f"""Generate {language} code{framework_text} for the following task:

{description}

Requirements:
- Write clean, well-documented code
- Include comments explaining key parts
- Follow best practices for {language}
- Make it production-ready

Provide only the code, no explanations."""

            response = self.client.chat.completions.create(
                model='gpt-4o',  # Используем GPT-4o для генерации кода
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка генерации кода: {e}")
            return None
    
    async def analyze_code(self, code: str, language: str = 'python') -> Optional[Dict]:
        """
        Анализ кода
        
        Args:
            code: Код для анализа
            language: Язык программирования
            
        Returns:
            Результаты анализа
        """
        try:
            prompt = f"""Analyze this {language} code and provide:

1. Code quality assessment (1-10)
2. Potential bugs or issues
3. Security concerns
4. Performance suggestions
5. Best practices violations

Code:
```{language}
{code}
```

Provide analysis in JSON format:
{{
    "quality_score": <1-10>,
    "bugs": ["list of potential bugs"],
    "security": ["security concerns"],
    "performance": ["performance suggestions"],
    "best_practices": ["violations"]
}}"""

            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a code review expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            import json
            result = response.choices[0].message.content
            
            # Извлекаем JSON из ответа
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            return json.loads(result)
            
        except Exception as e:
            print(f"❌ Ошибка анализа кода: {e}")
            return None
    
    async def fix_code(self, code: str, issue: str, language: str = 'python') -> Optional[str]:
        """
        Исправление кода
        
        Args:
            code: Код с проблемой
            issue: Описание проблемы
            language: Язык программирования
            
        Returns:
            Исправленный код
        """
        try:
            prompt = f"""Fix the following {language} code issue:

Issue: {issue}

Original code:
```{language}
{code}
```

Provide the fixed code with comments explaining the changes.
Provide only the code, no explanations outside the code."""

            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "You are an expert debugger."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка исправления кода: {e}")
            return None
    
    async def explain_code(self, code: str, language: str = 'python') -> Optional[str]:
        """
        Объяснение кода
        
        Args:
            code: Код для объяснения
            language: Язык программирования
            
        Returns:
            Объяснение кода
        """
        try:
            prompt = f"""Explain this {language} code in simple terms:

```{language}
{code}
```

Provide:
1. What the code does (high-level)
2. How it works (step-by-step)
3. Key concepts used
4. Potential use cases"""

            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a programming teacher."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка объяснения кода: {e}")
            return None
    
    async def refactor_code(self, code: str, language: str = 'python') -> Optional[str]:
        """
        Рефакторинг кода
        
        Args:
            code: Код для рефакторинга
            language: Язык программирования
            
        Returns:
            Отрефакторенный код
        """
        try:
            prompt = f"""Refactor this {language} code to improve:
- Readability
- Maintainability
- Performance
- Following best practices

Original code:
```{language}
{code}
```

Provide the refactored code with comments explaining improvements.
Provide only the code, no explanations outside the code."""

            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "You are a senior software engineer specializing in code refactoring."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка рефакторинга: {e}")
            return None
    
    async def generate_tests(self, code: str, language: str = 'python') -> Optional[str]:
        """
        Генерация тестов для кода
        
        Args:
            code: Код для которого нужны тесты
            language: Язык программирования
            
        Returns:
            Тесты
        """
        try:
            test_framework = {
                'python': 'pytest',
                'javascript': 'jest',
                'typescript': 'jest',
                'java': 'JUnit',
                'go': 'testing package'
            }.get(language, 'appropriate testing framework')
            
            prompt = f"""Generate comprehensive unit tests for this {language} code using {test_framework}:

```{language}
{code}
```

Include:
- Test cases for normal scenarios
- Edge cases
- Error handling tests
- Mock external dependencies if needed

Provide only the test code."""

            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "You are a test-driven development expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка генерации тестов: {e}")
            return None
