"""
Site Auditor - Модуль визуального контроля и QA
"""
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class SiteAuditorService:
    """Сервис для аудита сайтов и поиска ошибок"""
    
    def __init__(self, openai_client):
        self.openai = openai_client
        print("✅ Site Auditor (QA Тестировщик) инициализирован")

    async def audit_page(self, url: str) -> Dict:
        """
        Полный аудит страницы
        """
        try:
            # 1. Скачиваем страницу
            print(f"🕵️‍♂️ Сканирую сайт: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Botsi AI Tester)'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Сайт недоступен (Status: {response.status_code})"
                }
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Удаляем мусор (скрипты, стили), чтобы не перегружать AI
            for script in soup(["script", "style", "svg"]):
                script.decompose()
                
            text_content = soup.get_text()[:10000] # Ограничим контекст
            structure = str(soup.prettify())[:15000] # Структура
            
            # 2. Анализ через GPT-4o
            prompt = f"""Проведи QA аудит веб-страницы.

URL: {url}

Структура HTML:
{structure}

Текстовый контент:
{text_content}

Найди потенциальные проблемы:
1. UX/UI ошибки (нелогичная структура, пустые блоки).
2. Проблемы с контентом (рыбный текст 'lorem ipsum', ошибки).
3. Технические ошибки (битые ссылки, отсутствие alt, плохая семантика).
4. SEO проблемы (заголовки, мета).

Дай краткий отчет и список рекомендаций по исправлению."""

            gpt_response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты Senior QA Automation Engineer. Ты ищешь баги на сайтах."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            report = gpt_response.choices[0].message.content
            
            return {
                "success": True,
                "url": url,
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
