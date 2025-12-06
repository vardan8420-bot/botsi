"""
GitHub интеграция с реальным API
"""
from typing import Optional, Dict, List
from github import Github, GithubException


class GitHubManager:
    """Менеджер GitHub с реальной интеграцией"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация менеджера
        
        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.github = None
        self.user = None
        
        if token:
            try:
                self.github = Github(token)
                self.user = self.github.get_user()
                print(f"✅ GitHub подключен: @{self.user.login}")
            except Exception as e:
                print(f"⚠️ Ошибка подключения к GitHub: {e}")
                self.github = None
        else:
            print("⚠️ GitHub token не найден")
    
    def is_configured(self) -> bool:
        """Проверить настроен ли GitHub"""
        return self.github is not None
    
    async def get_user_info(self) -> Dict:
        """
        Получить информацию о пользователе
        
        Returns:
            Информация о пользователе GitHub
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'GitHub не настроен. Добавьте GITHUB_TOKEN.'
            }
        
        try:
            return {
                'success': True,
                'username': self.user.login,
                'name': self.user.name or self.user.login,
                'public_repos': self.user.public_repos,
                'followers': self.user.followers,
                'following': self.user.following
            }
        except GithubException as e:
            return {
                'success': False,
                'error': f'Ошибка GitHub API: {e.data.get("message", str(e))}'
            }
    
    async def list_repositories(self, limit: int = 10) -> Dict:
        """
        Список репозиториев пользователя
        
        Args:
            limit: Максимальное количество репозиториев
            
        Returns:
            Список репозиториев
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'GitHub не настроен'
            }
        
        try:
            repos = []
            for repo in self.user.get_repos()[:limit]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description or 'Нет описания',
                    'private': repo.private,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'url': repo.html_url
                })
            
            return {
                'success': True,
                'repositories': repos,
                'count': len(repos)
            }
        except GithubException as e:
            return {
                'success': False,
                'error': f'Ошибка: {e.data.get("message", str(e))}'
            }
    
    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False
    ) -> Dict:
        """
        Создание репозитория
        
        Args:
            name: Название репозитория
            description: Описание
            private: Приватный или публичный
            
        Returns:
            Информация о репозитории
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'GitHub не настроен'
            }
        
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=True  # Создать с README
            )
            
            return {
                'success': True,
                'name': repo.name,
                'url': repo.html_url,
                'message': f'Репозиторий {repo.full_name} создан!'
            }
        except GithubException as e:
            return {
                'success': False,
                'error': f'Ошибка: {e.data.get("message", str(e))}'
            }
    
    async def create_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str
    ) -> Dict:
        """
        Создание файла в репозитории
        
        Args:
            repo_name: Название репозитория (username/repo)
            file_path: Путь к файлу
            content: Содержимое файла
            commit_message: Сообщение коммита
            
        Returns:
            Результат операции
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'GitHub не настроен'
            }
        
        try:
            repo = self.github.get_repo(repo_name)
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content
            )
            
            return {
                'success': True,
                'file': file_path,
                'commit': result['commit'].sha[:7],
                'url': result['content'].html_url,
                'message': f'Файл {file_path} создан!'
            }
        except GithubException as e:
            return {
                'success': False,
                'error': f'Ошибка: {e.data.get("message", str(e))}'
            }
    
    async def get_repository_info(self, repo_name: str) -> Dict:
        """
        Информация о репозитории
        
        Args:
            repo_name: Название репозитория (username/repo)
            
        Returns:
            Информация о репозитории
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'GitHub не настроен'
            }
        
        try:
            repo = self.github.get_repo(repo_name)
            
            return {
                'success': True,
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description or 'Нет описания',
                'private': repo.private,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'language': repo.language,
                'url': repo.html_url,
                'created_at': repo.created_at.strftime('%Y-%m-%d'),
                'updated_at': repo.updated_at.strftime('%Y-%m-%d')
            }
        except GithubException as e:
            return {
                'success': False,
                'error': f'Ошибка: {e.data.get("message", str(e))}'
            }
