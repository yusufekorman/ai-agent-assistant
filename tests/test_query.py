import unittest
from unittest.mock import patch, MagicMock
import asyncio
from utils.query import query_llm

class TestQueryLLM(unittest.TestCase):
    def setUp(self):
        """Setup to run before each test"""
        self.test_config = {
            'llm_provider': 'lm_studio',
            'api_url': 'http://localhost:1234/v1',
            'llm_model': 'llama-3.2-3b-instruct',
            'temperature': 0.7,
            'max_tokens': 2000,
            'timeout': 30
        }
        self.test_prompt = "Test prompt"
        self.test_memory = ["Previous context 1", "Previous context 2"]
        self.test_system_ip = "127.0.0.1"
        self.test_system_prompt = "You are a helpful assistant"

    def run_async(self, coroutine):
        """Run asynchronous function synchronously"""
        return asyncio.run(coroutine)

    @patch('openai.OpenAI')
    async def test_lm_studio_query(self, mock_openai):
        """LM Studio query test"""
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        response = await query_llm(
            prompt=self.test_prompt,
            system_ip=self.test_system_ip,
            memory_vectors=self.test_memory,
            config=self.test_config,
            system_prompt=self.test_system_prompt
        )

        self.assertIsNotNone(response)
        self.assertIn("choices", response)
        self.assertEqual(response["choices"][0]["message"]["content"], "Test response")

        # API call checks
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["temperature"], 0.7)
        self.assertEqual(call_args["max_tokens"], 2000)

    @patch('openai.OpenAI')
    async def test_openai_query(self, mock_openai):
        """OpenAI query test"""
        # OpenAI configuration
        openai_config = self.test_config.copy()
        openai_config.update({
            'llm_provider': 'openai',
            'auth_token': 'test_token'
        })

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="OpenAI response"))
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        response = await query_llm(
            prompt=self.test_prompt,
            system_ip=self.test_system_ip,
            config=openai_config,
            system_prompt=self.test_system_prompt
        )

        self.assertIsNotNone(response)
        self.assertEqual(response["choices"][0]["message"]["content"], "OpenAI response")

        # Check OpenAI specific parameters
        mock_openai.assert_called_with(
            api_key='test_token',
            base_url=openai_config['api_url']
        )

    @patch('openai.OpenAI')
    async def test_context_handling(self, mock_openai):
        """Context handling test"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        test_memory = ["Memory 1", "Memory 2"]
        await query_llm(
            prompt=self.test_prompt,
            system_ip=self.test_system_ip,
            memory_vectors=test_memory,
            config=self.test_config
        )

        # Check context message
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        context_message = next(msg for msg in messages if "My IP address is" in msg["content"])
        self.assertIsNotNone(context_message)
        self.assertIn(self.test_system_ip, context_message["content"])
        self.assertIn("Memory 1", context_message["content"])
        self.assertIn("Memory 2", context_message["content"])

    async def test_missing_api_url(self):
        """Missing API URL test"""
        invalid_config = self.test_config.copy()
        del invalid_config['api_url']

        with self.assertRaises(ValueError) as context:
            await query_llm(
                prompt=self.test_prompt,
                system_ip=self.test_system_ip,
                config=invalid_config
            )
        self.assertIn("API URL", str(context.exception))

    async def test_missing_auth_token(self):
        """Missing OpenAI token test"""
        invalid_config = self.test_config.copy()
        invalid_config['llm_provider'] = 'openai'

        with self.assertRaises(ValueError) as context:
            await query_llm(
                prompt=self.test_prompt,
                system_ip=self.test_system_ip,
                config=invalid_config
            )
        self.assertIn("token", str(context.exception))

    @patch('openai.OpenAI')
    async def test_conversation_flow(self, mock_openai):
        """Conversation flow test"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Follow-up response"))
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        response = await query_llm(
            prompt="Initial prompt",
            answer="Initial response",
            prompt2="Follow-up question",
            system_ip=self.test_system_ip,
            config=self.test_config
        )

        # Check message order
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        message_contents = [msg["content"] for msg in messages if msg["role"] != "system"]
        
        self.assertIn("Initial prompt", message_contents)
        self.assertIn("Initial response", message_contents)
        self.assertIn("Follow-up question", message_contents)
        
        # Check ordering
        prompt_idx = message_contents.index("Initial prompt")
        answer_idx = message_contents.index("Initial response")
        prompt2_idx = message_contents.index("Follow-up question")
        
        self.assertTrue(prompt_idx < answer_idx < prompt2_idx)

    @patch('openai.OpenAI')
    async def test_error_handling(self, mock_openai):
        """Error handling test"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client

        response = await query_llm(
            prompt=self.test_prompt,
            system_ip=self.test_system_ip,
            config=self.test_config
        )

        self.assertIsNone(response)

def run_tests():
    """Run all tests"""
    unittest.main()

if __name__ == '__main__':
    run_tests()