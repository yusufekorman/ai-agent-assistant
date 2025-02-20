import unittest
from unittest.mock import patch, AsyncMock
import asyncio
import json
from utils.execute_response import execute_response, handle_system_command, handle_browser_command

class TestExecuteResponse(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak kurulum"""
        self.test_config = {
            'llm_model': 'llama-3.2-3b-instruct',
            'temperature': 0.7,
            'max_tokens': 150,
            'timeout': 30
        }
        self.test_context = {
            'secrets': {
                'weather_api_key': 'test_weather_key',
                'news_api_key': 'test_news_key'
            },
            'system_ip': '127.0.0.1'
        }

    def run_async(self, coroutine):
        """Asenkron fonksiyonu senkron olarak çalıştır"""
        return asyncio.run(coroutine)

    @patch('utils.tool_utils.get_weather')
    async def test_weather_need_request(self, mock_weather):
        """Hava durumu need request testi"""
        mock_weather.return_value = "Weather: 20°C, Clear sky"
        
        response_text = json.dumps({
            "response": "Let me check the weather",
            "need": "weather_forecast:Istanbul",
            "commands": ""
        })

        response = await execute_response(
            response_text,
            "What's the weather in Istanbul?",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIsInstance(response, str)
        mock_weather.assert_called_once_with("Istanbul", "test_weather_key")

    @patch('utils.tool_utils.get_news')
    async def test_news_need_request(self, mock_news):
        """Haber need request testi"""
        mock_news.return_value = "Latest news: Test headline"
        
        response_text = json.dumps({
            "response": "Here are the latest news",
            "need": "news:technology",
            "commands": ""
        })

        response = await execute_response(
            response_text,
            "Show me tech news",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIsInstance(response, str)
        mock_news.assert_called_once_with("technology", "test_news_key")

    @patch('utils.tool_utils.search_wikipedia')
    async def test_wiki_need_request(self, mock_wiki):
        """Wikipedia need request testi"""
        mock_wiki.return_value = "Wikipedia summary: Test article"
        
        response_text = json.dumps({
            "response": "Let me search Wikipedia",
            "need": "wiki:Artificial Intelligence",
            "commands": ""
        })

        response = await execute_response(
            response_text,
            "What is AI?",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIsInstance(response, str)
        mock_wiki.assert_called_once_with("Artificial Intelligence")

    async def test_handle_system_command_allowed(self):
        """İzin verilen sistem komutu testi"""
        cmd_type = "cmd"
        command = "echo test"
        
        result = await handle_system_command(cmd_type, command)
        self.assertIsInstance(result, str)

    async def test_handle_system_command_denied(self):
        """İzin verilmeyen sistem komutu testi"""
        cmd_type = "cmd"
        command = "rm -rf /"
        
        result = await handle_system_command(cmd_type, command)
        self.assertIn("security restrictions", result)

    @patch('webbrowser.open')
    async def test_handle_browser_command(self, mock_browser):
        """Tarayıcı komutu testi"""
        mock_browser.return_value = True
        
        url = "https://www.example.com"
        result = await handle_browser_command(url)
        self.assertIsNone(result)
        mock_browser.assert_called_once_with(url)

    async def test_invalid_json_response(self):
        """Geçersiz JSON yanıtı testi"""
        response_text = "Invalid JSON"
        
        response = await execute_response(
            response_text,
            "Test input",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIn("Invalid response format", response)

    async def test_empty_response(self):
        """Boş yanıt testi"""
        response_text = json.dumps({
            "response": "",
            "need": "",
            "commands": ""
        })
        
        response = await execute_response(
            response_text,
            "Test input",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertEqual(response, "")

    @patch('asyncio.create_subprocess_shell')
    async def test_system_command_timeout(self, mock_subprocess):
        """Sistem komutu zaman aşımı testi"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_subprocess.return_value = mock_process

        response_text = json.dumps({
            "response": "Running command",
            "need": "",
            "commands": "cmd:ping localhost -t"
        })

        response = await execute_response(
            response_text,
            "Run endless ping",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIn("Command execution timed out", response)

    async def test_invalid_need_format(self):
        """Geçersiz need format testi"""
        response_text = json.dumps({
            "response": "Testing",
            "need": "invalid_format",
            "commands": ""
        })

        response = await execute_response(
            response_text,
            "Test input",
            self.test_context,
            model=self.test_config['llm_model'],
            config=self.test_config
        )

        self.assertIn("Invalid need format", response)

def run_async_tests():
    """Asenkron testleri çalıştır"""
    async def run_all_tests():
        test_instance = TestExecuteResponse()
        test_instance.setUp()
        
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and 
                       asyncio.iscoroutinefunction(getattr(test_instance, method))]
        
        for test_name in test_methods:
            print(f"Running {test_name}...")
            await getattr(test_instance, test_name)()
            print(f"{test_name} completed successfully")

    asyncio.run(run_all_tests())

def run_tests():
    """Tüm testleri çalıştır"""
    unittest.main()

if __name__ == '__main__':
    run_tests()