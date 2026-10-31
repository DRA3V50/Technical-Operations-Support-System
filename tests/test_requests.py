import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

import database
from database import initialize, initialize_history
from request_service import (
    create_request,
    get_request,
    list_requests,
    update_request,
    close_request,
    get_request_history,
)


class TestSupportRequests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db = database.DB_PATH
        database.DB_PATH = (
            Path(self.temp_dir.name) / "test_toss.db"
        )

        initialize()
        initialize_history()

    def tearDown(self):
        database.DB_PATH = self.original_db
        self.temp_dir.cleanup()

    def create_sample(self):
        return create_request(
            "Employee cannot access shared folder",
            "IT Support",
            "Medium"
        )

    def test_create_request(self):
        request_id = self.create_sample()
        record = get_request(request_id)

        self.assertEqual(record["title"],
                         "Employee cannot access shared folder")
        self.assertEqual(record["status"], "Open")

    def test_request_persistence(self):
        request_id = self.create_sample()

        # A new connection must still find the record.
        record = get_request(request_id)
        self.assertIsNotNone(record)

    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            create_request(
                "Example issue", "IT Support", "Unknown"
            )

    def test_missing_title(self):
        with self.assertRaises(ValueError):
            create_request("", "IT Support", "Low")

    def test_update_assignment(self):
        request_id = self.create_sample()

        result = update_request(
            request_id, "Assigned", "IT Technician"
        )

        self.assertTrue(result)
        record = get_request(request_id)
        self.assertEqual(record["status"], "Assigned")
        self.assertEqual(record["assigned_to"], "IT Technician")

    def test_nonexistent_request(self):
        self.assertIsNone(get_request(9999))
        self.assertFalse(
            update_request(9999, "Assigned", "IT Technician")
        )

    def test_short_resolution_rejected(self):
        request_id = self.create_sample()

        with self.assertRaises(ValueError):
            close_request(request_id, "y")

        self.assertEqual(
            get_request(request_id)["status"], "Open"
        )

    def test_close_request(self):
        request_id = self.create_sample()

        result = close_request(
            request_id,
            "Test folder permissions restored successfully."
        )

        self.assertTrue(result)
        self.assertEqual(
            get_request(request_id)["status"], "Closed"
        )

    def test_duplicate_closure_rejected(self):
        request_id = self.create_sample()

        close_request(
            request_id,
            "Simulated access issue resolved successfully."
        )

        with self.assertRaises(ValueError):
            close_request(
                request_id,
                "Second closure attempt should be rejected."
            )

    def test_history_tracking(self):
        request_id = self.create_sample()

        update_request(
            request_id, "Assigned", "IT Technician"
        )

        close_request(
            request_id,
            "Simulated technical issue resolved successfully."
        )

        history = get_request_history(request_id)

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["action"], "Created")
        self.assertEqual(history[1]["action"], "Updated")
        self.assertEqual(history[2]["action"], "Closed")

    def test_list_requests(self):
        self.create_sample()

        records = list_requests()
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
