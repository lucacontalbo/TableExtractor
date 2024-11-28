import json
from io import StringIO

class PageFilteringTester(Tester):
    """
    task: define relevant keywords/keyphrases for each GRI label and check if at least one of the keywords/keyphrases is in the filtered pages
    """

    def __init__(self, gri_keywords_file):
        super(PageFilteringTester, self).__init__()
        self.tests = [self.get_keyword_in_content]
        with open(gri_keywords_file, 'r') as file:
            self.gri_keywords_file = json.load(file)
    
    def get_keyword_in_content(self, page_content, gri_label, table_structured):
        gri_label = gri_label.lower()
        page_content = page_content.lower()
        if gri_label not in self.gri_keywords.keys():
            raise AttributeError(f"\"{gri_label}\" is not a gri label")

        descr = self.gri_keywords[gri_label]
        for kw in descr.split(":")[0].split():
            if kw.lower() in page_content:
                return 1

        return 0

    def test_on_multiple_pages(self, page_contents, gri_label, table_structured):
        test_results = []
        for page_content in page_contents:
            test_results.append(self.test(page_content, gri_label, table_structured)[0])
        
        return sum(test_results) > 0


class TableExtractionTester(Tester):
    """
    Tasks:
    - Cell value detection: given the numerical values extracted from the page raw text, see if there's a match in the table given by GPT
    - Table structure detection: given the initial dataframe extracted by Unstructured (or other tools),
      extract the number of rows, columns and see if there is a match with the table given by GPT
    """

    def __init__(self,):
        super(TableExtractionTester, self).__init__()
        self.tests = [self.cell_value_detection, self.table_structure_detection]

    def get_numerical_values(self, string_with_numbers):
        pattern = r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'

        return re.findall(pattern, string_with_numbers)

    def cell_value_detection(self, page_content, gpt_table, table_structured):
        page_content = page_content.lower()

        numbers = self.get_numerical_values(gpt_table)
        match_counter = 0

        for num in numbers:
            if num.lower() in page_content:
                match_counter += 1

        return round(match_counter / len(numbers), 2)

    def table_structure_detection(self, page_content, gpt_table, table_structured):
        csv_string = StringIO(gpt_table)
        parsing_errors = 0
        try:
            df = pd.read_csv(csv_string, sep=";")
        except:
            parsing_errors += 1
        
        num_rows_gpt, num_cols_gpt = df.shape[0], df.shape[1]
        num_rows_tab, num_cols_tab = table_structured.shape[0], table_structured.shape[1]

        score_row = 1 if num_rows_gpt == num_rows_tab else 0
        score_col = 1 if num_cols_gpt == num_cols_tab else 0

        return score_row, score_col, parsing_errors

    def test_on_multiple_pages(self, page_contents, gpt_table, table_structured):
        test_results = []
        avg_cell_value, avg_score_row, avg_score_col, avg_parsing_errors = 0,0,0,0
        for page_content in page_contents:
            res = self.test(page_content, gpt_table, table_structured)
            avg_cell_value += res[0]
            avg_score_row += res[1][0]
            avg_score_col += res[1][1]
            avg_parsing_errors += res[1][2]

        avg_cell_value = round(avg_cell_value / len(page_contents), 2)
        avg_score_row = round(avg_score_row / len(page_contents), 2)
        avg_score_col = round(avg_score_col / len(page_contents), 2)
        avg_parsing_errors = round(avg_parsing_errors / len(page_contents), 2)

        return avg_cell_value, avg_score_row, avg_score_col, avg_parsing_errors

class Tester:
    def __init__(self,):
        pass

    def test(self, page_content, comparison_obj, table_structured):
        test_results = []
        for test_fn in self.tests:
            test_results.append(test_fn(page_content, comparison_obj, table_structured))
        
        return test_results

    