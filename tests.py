"""Tests for climate data project."""

import json
from unittest import TestCase
from server import app

class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_index(self):
        """Test index route."""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn('<title>Climate Data Visualization</title>', result.data)

    def test_reports_json(self):
        """Test json route."""

        result = self.client.post("/reports.json", data={'lat': 25.5})
        response_dict = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        # self.assertTrue(response_dict['success'])
        self.assertEqual(response_dict['lat'], 25.5)

if __name__ == '__main__':

    import unittest
    unittest.main()
