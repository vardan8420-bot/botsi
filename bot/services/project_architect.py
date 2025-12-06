"""
Project Architect - Модуль для создания полных веб-проектов
"""
from typing import Dict, List, Optional
import json
import asyncio
from bot.services.github_manager import GitHubManager


class ProjectArchitectService:
    """Сервис для генерации и деплоя полных проектов"""
    
    def __init__(self, openai_client, github_manager: GitHubManager):
        self.openai = openai_client
        self.github = github_manager
        print("✅ Project Architect (Создатель сайтов) инициализирован")

    async def create_website_structure(self, topic: str, user_wishes: str, language: str = 'ru') -> Dict:
        """
        1. Создает структуру файлов проекта
        """
        prompt = f"""Ты cтарший веб-архитектор. Твоя задача - спроектировать структуру сайта уровня Awwwards.

Тема сайта: {topic}
Пожелания: {user_wishes}
Язык контента: {language}

Требования к стеку:
- HTML5 (семантический)
- CSS3 (современный, Flexbox/Grid, анимации, Variables)
- Vanilla JavaScript (современный ES6+)
- БЕЗ внешних тяжелых фреймворков (React/Vue), чтобы сайт работал сразу просто открыв index.html.
- Можно использовать CDN (Tailwind, FontAwesome, Google Fonts).

Ответь ТОЛЬКО валидным JSON объектом следующей структуры:
{{
    "repo_name": "kebab-case-name",
    "description": "Short description",
    "files": [
        {{
            "path": "index.html",
            "description": "Что должно быть в этом файле (структура)"
        }},
        {{
            "path": "styles/main.css",
            "description": "Стилевые решения, цветовая гамма"
        }},
        {{
            "path": "js/app.js",
            "description": "Логика и анимации"
        }},
        {{
            "path": "README.md",
            "description": "Описание проекта для GitHub"
        }}
    ]
}}
"""
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты JSON генератор. Отвечай только чистым JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    async def generate_file_content(self, file_path: str, description: str, topic: str, language: str) -> str:
        """
        2. Генерирует контент конкретного файла
        """
        prompt = f"""Напиши ПОЛНЫЙ, рабочий, профессиональный код для файла: {file_path}

Проект: {topic}
Задача файла: {description}
Язык: {language}

ВАЖНО:
- Код должен быть готовым к продакшену.
- Если это HTML - сделай красивую структуру, подключи стили и скрипты.
- Используй красивые плейсхолдеры для картинок (например, source.unsplash.com).
- Добавь классные анимации и hover-эффекты.
- Не пиши комментариев типа "здесь ваш код", пиши ПОЛНЫЙ код.
"""
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты лучший веб-разработчик в мире. Ты пишешь идеальный код."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        code = response.choices[0].message.content
        # Очистка от маркдауна если есть
        code = code.replace("```html", "").replace("```css", "").replace("```javascript", "").replace("```", "")
        return code.strip()

    async def build_and_deploy_site(self, topic: str, user_wishes: str, language: str = 'ru') -> Dict:
        """
        ГЛАВНЫЙ МЕТОД: Планирует -> Кодит -> Деплоит
        """
        try:
            # 1. Планирование
            print(f"🏗️ Планирую архитектуру для: {topic}")
            plan = await self.create_website_structure(topic, user_wishes, language)
            
            repo_name = plan['repo_name']
            
            # 2. Создание репозитория
            print(f"📦 Создаю репозиторий: {repo_name}")
            repo_url = self.github.create_repo(repo_name, plan.get('description', topic))
            if not repo_url:
                return {"success": False, "error": "Не удалось создать репозиторий"}

            # 3. Генерация файлов (Параллельно!)
            print("⚡ Генерирую файлы...")
            files_to_create = {}
            
            tasks = []
            for file_info in plan['files']:
                tasks.append(
                    self.generate_file_content(file_info['path'], file_info['description'], topic, language)
                )
            
            # Ждем генерации всех файлов
            contents = await asyncio.gather(*tasks)
            
            for i, file_info in enumerate(plan['files']):
                files_to_create[file_info['path']] = contents[i]
            
            # 4. Заливка на GitHub
            print("🚀 Отправляю код на GitHub...")
            # Создаем файлы по одному (GitHub API ограничение, но быстро)
            uploaded_files = []
            for path, content in files_to_create.items():
                file_url = self.github.create_file(repo_name, path, content, f"feat: Add {path}")
                if file_url:
                    uploaded_files.append(path)
            
            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": repo_url,
                "files": uploaded_files,
                "deploy_url": f"https://{repo_name}.vercel.app" # Предсказание ссылки Vercel
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
