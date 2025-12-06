"""
Генерация изображений через DALL-E и Stable Diffusion
"""
from typing import Optional, Dict
import os
import requests
from io import BytesIO


class ImageGenerationService:
    """Сервис генерации изображений"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Инициализация сервиса
        
        Args:
            openai_api_key: OpenAI API ключ для DALL-E
        """
        self.openai_api_key = openai_api_key
        self.dalle_available = openai_api_key is not None
        
        if self.dalle_available:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_api_key)
                print("✅ DALL-E доступен")
            except Exception as e:
                print(f"⚠️ Ошибка DALL-E: {e}")
                self.dalle_available = False
        else:
            print("⚠️ DALL-E недоступен - нужен OPENAI_API_KEY")
        
        # Stable Diffusion (бесплатный API)
        self.sd_api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        print("✅ Stable Diffusion доступен (бесплатно)")
    
    async def generate_dalle(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict:
        """
        Генерация через DALL-E 3 (платно)
        
        Args:
            prompt: Описание изображения
            size: Размер (1024x1024, 1792x1024, 1024x1792)
            quality: Качество (standard, hd)
            
        Returns:
            URL изображения или ошибка
        """
        if not self.dalle_available:
            return {
                'success': False,
                'error': 'DALL-E недоступен. Добавьте OPENAI_API_KEY.'
            }
        
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            return {
                'success': True,
                'url': response.data[0].url,
                'revised_prompt': response.data[0].revised_prompt,
                'model': 'DALL-E 3'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка DALL-E: {str(e)}'
            }
    
    async def generate_sd(self, prompt: str) -> Dict:
        """
        Генерация через Stable Diffusion (бесплатно)
        
        Args:
            prompt: Описание изображения
            
        Returns:
            Байты изображения или ошибка
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }
            
            response = requests.post(
                self.sd_api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'image_bytes': response.content,
                    'model': 'Stable Diffusion XL'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка API: {response.status_code}'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка Stable Diffusion: {str(e)}'
            }
    
    async def generate(
        self,
        prompt: str,
        use_premium: bool = False,
        size: str = "1024x1024"
    ) -> Dict:
        """
        Универсальная генерация изображения
        
        Args:
            prompt: Описание
            use_premium: Использовать DALL-E (платно) или SD (бесплатно)
            size: Размер для DALL-E
            
        Returns:
            Результат генерации
        """
        if use_premium and self.dalle_available:
            # Платная версия DALL-E
            return await self.generate_dalle(prompt, size=size, quality="hd")
        else:
            # Бесплатная версия Stable Diffusion
            return await self.generate_sd(prompt)
