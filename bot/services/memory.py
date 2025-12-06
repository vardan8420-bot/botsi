"""
Долгосрочная память бота через Vector Database
"""
from typing import Optional, List, Dict
import os
import json


class MemoryService:
    """Сервис долгосрочной памяти"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Инициализация сервиса памяти
        
        Args:
            openai_api_key: OpenAI API ключ для embeddings
        """
        self.openai_api_key = openai_api_key
        self.is_available = openai_api_key is not None
        self.collection = None
        
        if self.is_available:
            try:
                import chromadb
                from chromadb.config import Settings
                
                # Инициализация ChromaDB
                self.client = chromadb.Client(Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                ))
                
                # Создаем коллекцию для памяти
                self.collection = self.client.get_or_create_collection(
                    name="user_memories",
                    metadata={"description": "Long-term user memories"}
                )
                
                print("✅ Долгосрочная память инициализирована (ChromaDB)")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации памяти: {e}")
                self.is_available = False
        else:
            print("⚠️ Память недоступна - нужен OPENAI_API_KEY")
    
    async def remember(
        self,
        user_id: int,
        fact: str,
        category: str = "general"
    ) -> Dict:
        """
        Запомнить факт о пользователе
        
        Args:
            user_id: ID пользователя
            fact: Факт для запоминания
            category: Категория (general, preference, project, goal)
            
        Returns:
            Результат операции
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Память недоступна'
            }
        
        try:
            # Создаем уникальный ID
            memory_id = f"{user_id}_{category}_{len(fact)}"
            
            # Сохраняем в ChromaDB
            self.collection.add(
                documents=[fact],
                metadatas=[{
                    "user_id": str(user_id),
                    "category": category
                }],
                ids=[memory_id]
            )
            
            return {
                'success': True,
                'message': f'Запомнил: {fact[:50]}...'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
    
    async def recall(
        self,
        user_id: int,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict:
        """
        Вспомнить факты о пользователе
        
        Args:
            user_id: ID пользователя
            query: Поисковый запрос (опционально)
            category: Категория (опционально)
            limit: Максимум результатов
            
        Returns:
            Список фактов
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Память недоступна'
            }
        
        try:
            # Фильтр по пользователю
            where_filter = {"user_id": str(user_id)}
            
            if category:
                where_filter["category"] = category
            
            if query:
                # Семантический поиск
                results = self.collection.query(
                    query_texts=[query],
                    where=where_filter,
                    n_results=limit
                )
            else:
                # Получить все факты
                results = self.collection.get(
                    where=where_filter,
                    limit=limit
                )
            
            memories = []
            if query:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    memories.append({
                        'fact': doc,
                        'category': meta.get('category', 'general')
                    })
            else:
                for doc, meta in zip(results['documents'], results['metadatas']):
                    memories.append({
                        'fact': doc,
                        'category': meta.get('category', 'general')
                    })
            
            return {
                'success': True,
                'memories': memories,
                'count': len(memories)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}',
                'memories': []
            }
    
    async def forget(self, user_id: int, category: Optional[str] = None) -> Dict:
        """
        Забыть факты о пользователе
        
        Args:
            user_id: ID пользователя
            category: Категория для удаления (опционально)
            
        Returns:
            Результат операции
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Память недоступна'
            }
        
        try:
            where_filter = {"user_id": str(user_id)}
            
            if category:
                where_filter["category"] = category
            
            # Получаем ID для удаления
            results = self.collection.get(where=where_filter)
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                
                return {
                    'success': True,
                    'message': f'Забыл {len(results["ids"])} фактов'
                }
            else:
                return {
                    'success': True,
                    'message': 'Нечего забывать'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
