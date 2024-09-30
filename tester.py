from gri_keywords import gri_keywords

class PageFilteringTester:
    """
    task: define relevant keywords/keyphrases for each GRI label and check if at least one of the keywords/keyphrases is in the filtered pages
    """

    def __init__(self,):
        self.tests = [self.get_keyword_in_content]
    
    def get_keyword_in_content(self, page_content, gri_label):
        gri_label = gri_label.lower()
        page_content = page_content.lower()
        if gri_label not in gri_keywords.keys():
            raise AttributeError(f"\"{gri_label}\" is not a gri label")

        for kw in gri_keywords[gri_label]:
            if kw.lower() in page_content:
                return 1

        return 0

    def test(self, page_content, gri_label):
        test_results = []
        for test_fn in self.tests:
            test_results.append(test_fn(page_content, gri_label))
        
        return test_results


class TableExtractionTester:
    """
    Tasks:
    - Cell value detection: given the numerical values extracted from the page raw text, see if there's a match in the table given by GPT
    - Table structure detection: given the initial dataframe extracted by Unstructured (or other tools),
      extract the number of rows, columns and see if there is a match with the table given by GPT
    """


    def __init__(self,):
        self.tests = [self.cell_value_detection, self.table_structure_detection]

    def get_numerical_values(self, string_with_numbers):
        pattern = r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'

        return re.findall(pattern, string_with_numbers)

    def cell_value_detection(self, page_content, gpt_table):
        page_content = page_content.lower()

        numbers = self.get_numerical_values(gpt_table)
        match_counter = 0

        for num in numbers:
            if num.lower() in page_content:
                match_counter += 1

        return round(match_counter / len(numbers), 2)

    def table_structure_detection(self, gpt_table, table_structured):
        pass

    def test(self, page_content, gpt_table, table_structured):

        test_results = []
        for test_fn in self.tests:
            test_results.append(test_fn(page_content, gpt_table))
        
        return test_results



class Tester:
    def __init__(self,):
        pass

    