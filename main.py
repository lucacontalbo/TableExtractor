from dotenv import load_dotenv

from utils import init_args
from runnable import Runnable
from open_ai import OpenAIChatModel
from table_extraction import UnstructuredTableExtractor
from prompts import system_prompt, human_prompt
from markdown_remover import MarkdownRemover
from tqdm import tqdm

import os
import csv
import json
import numpy as np

load_dotenv()

"""from onnxruntime.capi import _pybind_state as C
print(f"Available ONNXRT providers: {C.get_available_providers()}")
print(a)"""

if __name__ == "__main__":
    args = init_args()
    r = Runnable(args)

    if len(args["load_query_from_file"]) > 0:
      md_remover = MarkdownRemover()
      openai_model = OpenAIChatModel(os.environ["OPENAI_MODEL_NAME"], float(os.environ["OPENAI_TEMPERATURE"]))
      with open(f"{args['load_query_from_file']}", 'r') as file:
        data = json.load(file)
      
      if os.path.isdir(args["pdf"]):
        file_names = os.listdir(args["pdf"])
      elif os.path.isfile(args["pdf"]):
        file_names = [args["pdf"]]
      else:
        raise ValueError(f"wrong file name")
  
      for file_name in file_names:
        splitted_file_name = file_name.split(".")
        if splitted_file_name[-1] != "pdf":
          continue
        
        dir_name = '.'.join(splitted_file_name[:-1])

        if os.path.exists(f"table_dataset/{dir_name}"):
          continue

        args["pdf"] = os.path.join(args["pdf"], file_name)
        gri_code_to_page = {}
        tables_as_html = set()

        for i, (gri_code, description) in enumerate(data.items()):
          if gri_code not in gri_code_to_page.keys():
            gri_code_to_page[gri_code] = []

          args["query"] = description
          r.set_args(args)
          s = r.run()

          ute = UnstructuredTableExtractor("yolox", "hi_res")

          for doc in tqdm(s[:20]):
            tables = ute.extract_table_unstructured([doc])

            for table in tables:
              tables_as_html.add((table[0].metadata.text_as_html, doc.page_content, doc.metadata["page"], table[-1]))
              gri_code_to_page[gri_code].append((doc.metadata["page"], table[-1]))

        openai_results = []
        for j, table_html in enumerate(tables_as_html):
          res = openai_model.invoke(
              system_prompt,
              human_prompt.format(table_html[0], table_html[1])
          )

          if not os.path.exists(f"table_dataset/{dir_name}"):
            os.mkdir(f"table_dataset/{dir_name}")

          content = md_remover.unmark(res.content)

          with open(f'table_dataset/{dir_name}/{str(table_html[-2])}_{str(table_html[-1])}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([content])

        with open(f'table_dataset/{dir_name}/metadata.json', 'w') as json_file:
          json.dump(gri_code_to_page, json_file, indent=4)
        args["pdf"] = "/".join(args["pdf"].split("/")[:-1])
    else:
      s = r.run()
