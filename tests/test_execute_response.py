import unittest
from unittest.mock import patch, MagicMock
import asyncio
from utils.execute_response import execute_response

class TestExecuteResponse(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak kurulum"""
        self.test_config = {
            'llm_model': 'llama-3.2-3b-instruct'
        }
        self.test_context = {
            'secrets': {
                'weather_api_key': 'test_key',
                'news_api_key': 'test_key'
            },
            'system_ip': '127.0.0.1'
        }

    def run_async(self, coroutine):
        """Asenkron fonksiyonu senkron olarak çalıştır"""
        return asyncio.run(coroutine)

    @patch('requests.get')
    def test_weather_command(self, mock_get):
        """Hava durumu komutunun testi"""
        # Mock API yanıtı
        mock_get.return_value.json.return_value = {
            'main': {'temp': 20, 'humidity': 65},
            'weather': [{'description': 'clear sky'}]
        }
        mock_get.return_value.status_code = 200

        response = self.run_async(execute_response(
            "Checking weather in Istanbul",
            "What's the weather in Istanbul?",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        ))

        self.assertIsInstance(response, str)
        self.assertIn("Istanbul", response)

    @patch('requests.get')
    def test_news_command(self, mock_get):
        """Haber komutunun testi"""
        # Mock API yanıtı
        mock_get.return_value.json.return_value = {
            'articles': [
                {'title': 'Test News 1', 'description': 'Test Description 1'},
                {'title': 'Test News 2', 'description': 'Test Description 2'}
            ]
        }
        mock_get.return_value.status_code = 200

        response = self.run_async(execute_response(
            "Getting latest technology news",
            "Show me tech news",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        ))

        self.assertIsInstance(response, str)
        self.assertIn("news", response.lower())

    def test_basic_response(self):
        """Temel yanıt testi"""
        response = self.run_async(execute_response(
            "Hello! How can I help you?",
            "Hello",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        ))

        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_invalid_command(self):
        """Geçersiz komut testi"""
        response = self.run_async(execute_response(
            "EXECUTE_INVALID_COMMAND",
            "Do something invalid",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        ))

    @patch('subprocess.Popen')
    async def test_system_command(self, mock_popen):
        """Sistem komutu testi"""
        mock_popen.return_value.communicate.return_value = (b"Test output", b"")
        mock_popen.return_value.returncode = 0

        response = await execute_response(
            "EXECUTE_SYSTEM_COMMAND: echo test",
            "Run echo test",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIsInstance(response, str)
        self.assertIn("executed", response.lower())

    def test_empty_response(self):
        """Boş yanıt testi"""
        async def run_test():
            with self.assertRaises(ValueError):
                await execute_response(
                    "",
                    "Test input",
                    self.test_context,
                    model=self.test_config['llm_model'],
                    config=self.test_config
                )

        asyncio.run(run_test())

def run_async_tests():
    """Asenkron testleri çalıştır"""
    async def run_all_tests():
        test_cases = [
            'test_weather_command',
            'test_news_command',
            'test_basic_response',
            'test_invalid_command',
            'test_system_command'
        ]
        
        test_instance = TestExecuteResponse()
        test_instance.setUp()
        
        for test_name in test_cases:
            print(f"Running {test_name}...")
            await getattr(test_instance, test_name)()

    asyncio.run(run_all_tests())

def run_tests():
    """Tüm testleri çalıştır"""
    unittest.main()

if __name__ == '__main__':
    run_tests()