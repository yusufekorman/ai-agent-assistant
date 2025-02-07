import unittest
from unittest.mock import patch, MagicMock
import asyncio
from utils.query import query_llm

class TestQueryLMStudio(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            'lm_studio_completions_url': 'http://localhost:1234/v1/chat/completions',
            'llm_model': 'llama-3.2-3b-instruct'
        }
        self.test_prompt = "Test prompt"
        self.test_memory = ["Previous context 1", "Previous context 2"]
        self.test_system_ip = "127.0.0.1"

    @patch('aiohttp.ClientSession')
    async def test_successful_query(self, mock_session):
        # Mock başarılı bir API yanıtını simüle et
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value={
            "choices": [{"message": {"content": "Test response"}}]
        })
        
        mock_session.return_value.__aenter__.return_value.post = MagicMock(
            return_value=mock_response
        )

        response = await query_llm(
            prompt=self.test_prompt,
            memory_vectors=self.test_memory,
            system_ip=self.test_system_ip,
            config=self.test_config
        )

        self.assertIsNotNone(response, "Response should not be None")
        if not isinstance(response, dict):
            self.fail("Response should be a dictionary")
        self.assertIn("choices", response, "Response should contain 'choices' key")
        self.assertIsInstance(response["choices"], list, "Choices should be a list")
        self.assertGreater(len(response["choices"]), 0, "Choices should not be empty")
        self.assertEqual(response["choices"][0]["message"]["content"], "Test response")

    @patch('aiohttp.ClientSession')
    async def test_failed_query(self, mock_session):
        # API hatası durumunu simüle et
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = MagicMock(return_value="Internal Server Error")
        
        mock_session.return_value.__aenter__.return_value.post = MagicMock(
            return_value=mock_response
        )

        with self.assertRaises(Exception):
            await query_llm(
                prompt=self.test_prompt,
                memory_vectors=self.test_memory,
                system_ip=self.test_system_ip,
                config=self.test_config
            )

    @patch('aiohttp.ClientSession')
    async def test_invalid_config(self, mock_session):
        # Geçersiz yapılandırma durumunu test et
        invalid_config = {}
        
        with self.assertRaises(KeyError):
            await query_llm(
                prompt=self.test_prompt,
                memory_vectors=self.test_memory,
                system_ip=self.test_system_ip,
                config=invalid_config
            )

    def test_empty_prompt(self):
        # Boş prompt durumunu test et
        async def run_test():
            with self.assertRaises(ValueError):
                await query_llm(
                    prompt="",
                    memory_vectors=self.test_memory,
                    system_ip=self.test_system_ip,
                    config=self.test_config
                )
        
        asyncio.run(run_test())

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()