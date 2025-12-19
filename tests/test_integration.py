import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
from src.processor import Processor

class TestGmailApiCli(unittest.TestCase):
    def setUp(self):
        # Mocks for dependencies
        self.mock_client = MagicMock()
        self.mock_processor = MagicMock()
        self.mock_formatter = MagicMock()
        self.app = Processor(
            client=self.mock_client,
            processor=self.mock_processor,
            formatter=self.mock_formatter
        )

    def test_run_new_messages(self):
        # Setup
        # We process 2 days: 2025-12-01 and 2025-12-02
        # On day 1, we find 'msg1'. On day 2, we find nothing.
        
        # Search called twice. 
        # Call 1 (Day 1): returns [{'id': 'msg1'}]
        # Call 2 (Day 2): returns []
        self.mock_client.search_messages.side_effect = [[{'id': 'msg1'}], []]
        # Cache load called twice.
        # Call 1 (Day 1): returns [] (empty cache)
        # Call 2 (Day 2): returns [] (empty cache)
        with patch.object(Processor, '_load_cache', side_effect=[[], []]) as mock_load:
            # Get detail called for 'msg1'
            self.mock_client.get_message_detail.return_value = {'id': 'msg1', 'snippet': 'test'}
            # Save cache called for Day 1 (because new msg found). 
            # Day 2 has no messages, so no save if list is empty? Or we might save empty list if we want to cache "no mail"? 
            # Current logic: "if missing_ids:" -> save. If no missing ids, no save.
            # Day 1: missing_ids={'msg1'} -> save.
            # Day 2: current_ids={}, cached_ids={}, missing_ids={} -> no save.
            with patch.object(Processor, '_save_cache') as mock_save:
                # Run
                self.app.run('2025-12-01', '2025-12-02', 'INBOX')
                # Assertions
                # Check search called twice
                self.assertEqual(self.mock_client.search_messages.call_count, 2)
                # Check fetch missing
                self.mock_client.get_message_detail.assert_called_with('msg1')
                # Check save cache called once for Day 1
                mock_save.assert_called_once()
                args, _ = mock_save.call_args
                self.assertIn('20251201', args[0]) # filename check
                self.assertEqual(len(args[1]), 1) # 1 message in list
                self.assertEqual(args[1][0]['id'], 'msg1')
                # Check processing with accumulated results
                self.mock_processor.process_threads.assert_called()
                # args[0] passed to process_threads should contain msg1
                process_args = self.mock_processor.process_threads.call_args[0][0]
                self.assertEqual(len(process_args), 1)
                self.assertEqual(process_args[0]['id'], 'msg1')
                self.mock_processor.deduplicate_thread_content.assert_called()
                self.mock_formatter.generate_report.assert_called()

    def test_run_cached_messages(self):
        # Setup
        # Day 1: msg1 in Gmail, msg1 in Cache.
        self.mock_client.search_messages.return_value = [{'id': 'msg1'}]
        cached_data = [{'id': 'msg1', 'snippet': 'cached'}]
        # Load returns cached data
        with patch.object(Processor, '_load_cache', return_value=cached_data) as mock_load:
            with patch.object(Processor, '_save_cache') as mock_save:
                # Run for single day
                self.app.run('2025-12-01', '2025-12-01', 'INBOX')
                # Assertions
                # Should NOT fetch details
                self.mock_client.get_message_detail.assert_not_called()
                # Should not save
                mock_save.assert_not_called()
                # Should processing happen? Yes.
                self.mock_processor.process_threads.assert_called()
                process_args = self.mock_processor.process_threads.call_args[0][0]
                self.assertEqual(len(process_args), 1)
                self.assertEqual(process_args[0]['snippet'], 'cached')
                
    def test_load_cache_logic(self):
        # Test the actual file reading logic separately
        with patch('builtins.open', unittest.mock.mock_open(read_data='[{"id": "1"}]')) as m:
            with patch('os.path.exists', return_value=True):
                data = self.app._load_cache('dummy.json')
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['id'], '1')

    def test_save_cache_logic(self):
        with patch('builtins.open', unittest.mock.mock_open()) as m:
            data = [{'id': '1'}]
            self.app._save_cache('dummy.json', data)
            m.assert_called_with('dummy.json', 'w', encoding='utf-8')
            # Check write content... json dump writes string chunks
            handle = m()
            handle.write.assert_called()

if __name__ == '__main__':
    unittest.main()
