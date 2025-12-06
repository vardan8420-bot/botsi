"""
Поиск в интернете через Tavily API
"""
from typing import Optional, List, Dict
import os


class WebSearchService:
    """Сервис поиска в интернете"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация сервиса
        
        Args:
            api_key: Tavily API ключ
        """
        self.api_key = api_key
        self.is_available = api_key is not None
        
        if self.is_available:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=api_key)
                print("✅ Web Search подключен (Tavily)")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации Tavily: {e}")
                self.is_available = False
        else:
            print("⚠️ TAVILY_API_KEY не найден - поиск недоступен")
    
    async def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Поиск в интернете
        
        Args:
            query: Поисковый запрос
            max_results: Максимум результатов
            
        Returns:
            Результаты поиска
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Поиск недоступен. Добавьте TAVILY_API_KEY.'
            }
        
        try:
            # Поиск через Tavily
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            results = []
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'score': item.get('score', 0)
                })
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка поиска: {str(e)}'
            }
    
    async def get_answer(self, question: str) -> Dict:
        """
        Получить прямой ответ на вопрос
        
        Args:
            question: Вопрос
            
        Returns:
            Ответ с источниками
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Поиск недоступен'
            }
        
        try:
            # Поиск с ответом
            response = self.client.qna_search(query=question)
            
            return {
                'success': True,
                'question': question,
                'answer': response.get('answer', ''),
                'sources': response.get('results', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
