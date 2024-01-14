import argparse
import os
import xml.etree.ElementTree as ET
import sys

from html import escape


class GoogleTestParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.test_results = []

    def parse_xml(self):
        """
        # Parse the XML file and extracts the test results
        :return: void
        """
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Error parsing XML file {self.xml_file}: {e}")

        for testcase in root.iter("testcase"):
            test_case_name = testcase.get("name")
            test_case_status = "pass" if len(list(testcase)) == 0 else "fail"
            test_case_time = float(testcase.get("time", 0.0))

            self.test_results.append({
                "name": test_case_name,
                "status": test_case_status,
                "time": test_case_time,
            })


class HtmlReportGenerator:
    def __init__(self, test_results_list, xml_files, html_file, title):
        self.test_results_list = test_results_list
        self.xml_files = xml_files
        self.html_file = html_file
        self.title = title
        self.report_file = None

    def generate_html_report(self):
        """
        The main function that handles building the HTML report
        :return: void everything is written to the report file
        """
        with open(self.html_file, "w") as self.report_file:
            # Write HTML header and include CSS styles
            self.report_file.write("<html>\n")
            self.report_file.write("<head>\n")
            # Writes title for browser tab
            self.write_title()
            self.write_css_styles()
            self.report_file.write("</head>\n")
            self.report_file.write("<body>\n")
            self.report_file.write("<div class='container'>\n")

            # Generate visible title on the HTML page
            self.write_page_title()

            # Generate summary for each test file
            self.generate_summary()

            # Generate detailed results
            self.write_test_details()

            self.report_file.write("</div>\n")
            self.report_file.write("</body>\n")
            self.report_file.write("</html>\n")

    def write_page_title(self):
        """
        Writes the title as h1 heading if self.title is defined
        :return: void everything is written to the report file
        """
        if self.title:
            self.report_file.write(f"<h1>{escape(self.title)}</h1>\n")
        else:
            self.report_file.write("<h1>GoogleTest HTML Report</h1>\n")

    def write_title(self):
        """
        Writes the tab title if self.title is defined
        :return: void everything is written to the report file
        """
        if self.title:
            self.report_file.write(f"<title>{escape(self.title)}</title>\n")
        else:
            self.report_file.write("<title>GoogleTest HTML Report</title>\n")

    def write_css_styles(self):
        """
        Writes the css style for the HTML report directly into the html file,
        which makes it so an extra .css file is not required
        :return: void everything is written to the report file
        """
        self.report_file.write("<style>\n")
        self.report_file.write("body {\n")
        self.report_file.write("    font-family: Arial, sans-serif;\n")
        self.report_file.write("    background-color: #f4f4f4;\n")
        self.report_file.write("}\n")
        self.report_file.write(".container {\n")
        self.report_file.write("    max-width: 800px;\n")
        self.report_file.write("    margin: auto;\n")
        self.report_file.write("    background-color: white;\n")
        self.report_file.write("    padding: 20px;\n")
        self.report_file.write("    border: 1px solid #ddd;\n")
        self.report_file.write("    border-radius: 5px;\n")
        self.report_file.write("    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);\n")
        self.report_file.write("}\n")
        self.report_file.write("table {\n")
        self.report_file.write("    width: 100%;\n")
        self.report_file.write("    border-collapse: collapse;\n")
        self.report_file.write("    margin-bottom: 20px;\n")
        self.report_file.write("    background-color: #fff;\n")
        self.report_file.write("}\n")
        self.report_file.write("th, td {\n")
        self.report_file.write("    padding: 12px;\n")
        self.report_file.write("    border: 1px solid #ddd;\n")
        self.report_file.write("    text-align: left;\n")
        self.report_file.write("}\n")
        self.report_file.write("th {\n")
        self.report_file.write("    background-color: #f2f2f2;\n")
        self.report_file.write("}\n")
        self.report_file.write("td {\n")
        self.report_file.write("    font-weight: bold;\n")
        self.report_file.write("}\n")
        self.report_file.write("td.pass, th.pass {\n")
        self.report_file.write("    color: green;\n")
        self.report_file.write("}\n")
        self.report_file.write("td.fail, th.fail {\n")
        self.report_file.write("    color: red;\n")
        self.report_file.write("}\n")
        self.report_file.write("th:first-child, td:first-child {\n")
        self.report_file.write("    width: 30%;\n")
        self.report_file.write("}\n")
        self.report_file.write("th:nth-child(2), td:nth-child(2) {\n")
        self.report_file.write("    width: 15%;\n")
        self.report_file.write("}\n")
        self.report_file.write("th:nth-child(3), td:nth-child(3) {\n")
        self.report_file.write("    width: 15%;\n")
        self.report_file.write("}\n")
        self.report_file.write("th:nth-child(4), td:nth-child(4) {\n")
        self.report_file.write("    width: 15%;\n")
        self.report_file.write("}\n")
        self.report_file.write("th:nth-child(5), td:nth-child(5) {\n")
        self.report_file.write("    width: 25%;\n")
        self.report_file.write("}\n")
        self.report_file.write("hr {\n")
        self.report_file.write("    border: 1px solid #ddd;\n")
        self.report_file.write("}\n")
        self.report_file.write("</style>\n")

    def generate_summary(self):
        """
        Generate a summary table at the top of the HTML report file for both a single
        results file or a set of results files
        :return: void everything is written to the report file
        """
        # Generate a summary table for each test file
        self.report_file.write("<h2>Summary</h2>\n")
        self.report_file.write("<table>\n")
        self.report_file.write(
            "<tr><th>Test File</th>"
            "<th>Total Tests</th>"
            "<th>Passed</th>"
            "<th>Failed</th>"
            "<th>Total Execution Time</th></tr>\n")

        for i, test_results in enumerate(self.test_results_list):
            total_tests = len(test_results)
            total_passed = sum(1 for test in test_results if test['status'] == 'pass')
            total_failed = total_tests - total_passed
            total_time = sum(test['time'] for test in test_results)

            self.report_file.write("<tr>\n")
            self.report_file.write(f"<td>{os.path.basename(self.xml_files[i])}</td>\n")
            self.report_file.write(f"<td>{total_tests}</td>\n")
            self.report_file.write(f"<td>{total_passed}</td>\n")
            self.report_file.write(f"<td>{total_failed}</td>\n")
            self.report_file.write(f"<td>{total_time:.2f} seconds</td>\n")
            self.report_file.write("</tr>\n")

        self.report_file.write("</table>\n")
        self.report_file.write("<hr>\n")

    def write_test_details(self):
        """
        Writes the test details to the HTML report file for each test file or
        series of test files in the test results directory
        :return: void everything is written to the report file
        """
        # Generate detailed results for each test file
        for i, test_results in enumerate(self.test_results_list):
            self.report_file.write(f"<h2>Test Run {i + 1}</h2>\n")
            self.report_file.write("<table>\n")
            self.report_file.write("<tr><th>Test Case</th><th>Status</th><th>Time (s)</th></tr>\n")

            for result in test_results:
                self.report_file.write("<tr>\n")
                self.report_file.write(f"<td>{escape(result['name'])}</td>\n")
                self.report_file.write(f"<td class='{result['status']}'>{result['status']}</td>\n")
                self.report_file.write(f"<td>{result['time']}</td>\n")
                self.report_file.write("</tr>\n")

            self.report_file.write("</table>\n")


def main(args=None):
    """
    Main function that handles the command line arguments and calls the report generator function
    :return: void
    """
    if args is None:
        args = sys.argv[1:]

    project_dir = os.path.dirname(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description="Generate HTML report from GoogleTest XML files.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("gtest_path",
                        help="Directory or file path to process")
    parser.add_argument("--output",
                        help="HTML file path of the output HTML report file (default: %(default)s)",
                        default=os.path.join(project_dir, "gen_reports\\gtest_results.html"))
    parser.add_argument("--title",
                        help="Title of the HTML report",
                        default="Google Test Results")

    args = parser.parse_args()

    # create default directory if it doesn't exist
    if (args.output == "gen_reports\\gtest_results.html" and
            not os.path.exists(os.path.dirname(args.output))):
        os.makedirs(os.path.dirname(args.output))

    try:
        if os.path.isdir(args.gtest_path):
            # Process all XML files in the directory
            xml_files = [os.path.join(args.gtest_path, file)
                         for file in os.listdir(args.gtest_path) if file.endswith(".xml")]
        elif os.path.isfile(args.gtest_path) and args.gtest_path.endswith(".xml"):
            # Process the specified XML file
            xml_files = [args.gtest_path]
            args.title = os.path.basename(args.gtest_path)
        else:
            raise ValueError("Invalid input. Please provide a directory or a valid XML file.")

        # Parse XML files
        test_results_list = []
        for xml_file in xml_files:
            parser = GoogleTestParser(xml_file)
            parser.parse_xml()
            test_results_list.append(parser.test_results)

        # Generate HTML report
        report_title = args.title
        report_generator = HtmlReportGenerator(test_results_list, xml_files, args.output, report_title)
        report_generator.generate_html_report()

        # Print a success message
        print(f"HTML report generated successfully: {args.output}")
        return 0

    except ValueError as ve:
        print(f"Error: {ve}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
