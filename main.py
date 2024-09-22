from dotenv import load_dotenv

from utils import init_args
from runnable import Runnable
from open_ai import OpenAIChatModel
from table_extraction import UnstructuredTableExtractor
from prompts import system_prompt, human_prompt

import os

load_dotenv()

if __name__ == "__main__":
    args = init_args()
    r = Runnable(args)
    s = r.run()

    ute = UnstructuredTableExtractor("yolox", "hi_res")
    tables = ute.extract_table_unstructured([s[5]])
    tables_as_html = []

    for table in tables:
        tables_as_html.append(table[0].metadata.text_as_html)

    openai_model = OpenAIChatModel(os.environ["OPENAI_MODEL_NAME"], float(os.environ["OPENAI_TEMPERATURE"]))
    openai_results = []
    for table_metadata, table_html in zip(tables, tables_as_html):
        print(f"Source {table_metadata[1]} ------ Page {table_metadata[2]}")
        print(table_html)
        print(s[5].page_content)
        #print(a)
        res = openai_model.invoke(
            system_prompt,
            human_prompt.format(table_html, s[5].page_content) #s[table_metadata[-1]].page_content
        )
        print(res.content)
    #print(result)
