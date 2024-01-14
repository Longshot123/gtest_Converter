import argparse
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open

from src.googleTestXmlToHtmlConverter import GoogleTestParser, HtmlReportGenerator, main

# Import StringIO from the io module
from io import StringIO


class TestGoogleTestParser(unittest.TestCase):
    def test_parse_xml(self):
        xml_content = """
        <testsuites>
            <testsuite name="example_tests" tests="2">
                <testcase name="test_pass" />
                <testcase name="test_fail">
                    <failure message="Test failed" />
                </testcase>
            </testsuite>
        </testsuites>
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_xml:
            temp_xml.write(xml_content)
            temp_xml.seek(0)

            parser = GoogleTestParser(temp_xml.name)
            parser.parse_xml()

            self.assertEqual(len(parser.test_results), 2)
            self.assertEqual(parser.test_results[0]['name'], 'test_pass')
            self.assertEqual(parser.test_results[0]['status'], 'pass')
            self.assertEqual(parser.test_results[1]['name'], 'test_fail')
            self.assertEqual(parser.test_results[1]['status'], 'fail')


class TestHtmlReportGenerator(unittest.TestCase):
    def test_generate_html_report(self):
        test_results_list = [
            [{'name': 'test_pass', 'status': 'pass', 'time': 1.0}],
            [{'name': 'test_fail', 'status': 'fail', 'time': 2.0}]
        ]
        xml_files = ['test_file_1.xml', 'test_file_2.xml']
        html_file = 'test_report.html'
        title = 'Test Report'

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_report:
            # Use context manager to open the file
            with open(temp_report.name, 'w') as report_file:
                with patch('builtins.open', return_value=report_file):
                    generator = HtmlReportGenerator(test_results_list, xml_files, html_file, title)
                    generator.generate_html_report()

                    temp_report.seek(0)
                    report_content = temp_report.read()

                    # Simplified assertion
                    self.assertIn('<h1>Test Report</h1>', report_content)

    def test_write_page_title(self):
        # Instantiate HtmlReportGenerator with mock data
        test_results_list = [
            [{"name": "test_case_1", "status": "pass", "time": 1.0}],
            [{"name": "test_case_2", "status": "fail", "time": 2.0}]
        ]
        xml_files = ['test_file_1.xml', 'test_file_2.xml']
        html_file = 'output.html'
        title = 'Test Report'
        report_generator = HtmlReportGenerator(test_results_list, xml_files, html_file, title)

        # Use a custom StringIO object to capture writes
        with patch('builtins.open', create=True) as mock_open:
            fake_file = StringIO()
            mock_open.return_value.__enter__.return_value = fake_file

            # Call generate_html_report to initialize report_file
            with open(html_file, 'w') as fake_html_file:
                report_generator.report_file = fake_html_file
                report_generator.write_page_title()

            # Access the custom StringIO's content
            actual_content = fake_file.getvalue()

            # Assert the expected content
            expected_content = f"<h1>{title}</h1>\n"
            self.assertIn(expected_content, actual_content)

    def test_write_title(self):
        # Instantiate HtmlReportGenerator with mock data
        test_results_list = [
            [{"name": "test_case_1", "status": "pass", "time": 1.0}],
            [{"name": "test_case_2", "status": "fail", "time": 2.0}]
        ]
        xml_files = ['test_file_1.xml', 'test_file_2.xml']
        html_file = 'output.html'
        title = 'Test Report'
        report_generator = HtmlReportGenerator(test_results_list, xml_files, html_file, title)

        # Use a custom StringIO object to capture writes
        with patch('builtins.open', create=True) as mock_open:
            fake_file = StringIO()
            mock_open.return_value.__enter__.return_value = fake_file

            # Call generate_html_report to initialize report_file
            with open(html_file, 'w') as fake_html_file:
                report_generator.report_file = fake_html_file
                report_generator.write_title()

            # Access the custom StringIO's content
            actual_content = fake_file.getvalue()

            # Assert the expected content
            expected_content = f"<title>{title}</title>\n"
            self.assertIn(expected_content, actual_content)


class TestMainFunction(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.argv', ['googleTestXmlToHtmlConverter.py', '../test_results', '--output', 'output.html'])
    def test_main_with_args(self, mock_stdout):
        # Call the main function within the context of the patched sys.argv
        exit_code = main(sys.argv)

        # Ensure sys.exit was called with the expected argument (0 in this case)
        self.assertEqual(exit_code, 0)
        self.assertIn('HTML report generated successfully:', mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
