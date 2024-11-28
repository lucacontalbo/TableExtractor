import pandas as pd
import json
import csv
from copy import deepcopy
from dotenv import load_dotenv
import ast
from langchain_openai import ChatOpenAI

load_dotenv()

new_dataset = [["pdf name", "gri", "page nbr", "table nbr", "question", "value"]]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # api_key="...",  # if you prefer to pass api key in directly instaed of using env vars
    # base_url="...",
    # organization="...",
    # other params...
)

#prompt = """You will be given a table (in HTML) and some indicators.
#Extract the values that can reply the given indicators. Then, for each value, generate an unambiguous question that can be replied by the value. The generated question must have a different form than the indicators, but their meanings must be the same.
#By unambiguous question I mean that, based on the table, the question can have only one answer.
#In the questions, you must always specify the column indicator (when possible). If the column indicators are years, use different years when generating the questions (e.g. 2023, 2022, 2021 etc.)
#Morevover, in the questions, you must always specify the unit of measure in the request (if it is known, otherwise do not specify anything).
#As output, provide a Python dictionary that has the questions as keys and the extracted values are the values of the dictionary. Do not write anything else. Do not provide any Markdown formatting.

#Table: {}
#Topics: {}"""

prompt = """You will be given a table (in HTML) and some indicators.
Extract the values that can reply the given indicators. Then, for each value, generate an unambiguous question that can be replied by the value.
By unambiguous question I mean that, based on the table, the question can have only one answer.
In particular, the question must ask aggregation operations like summation, difference or percentage increase/decrease of values across different columns (e.g. across different years).
For example, you can ask "What's the total amount of X across the years?" or "What's the difference of X between YEAR1 and YEAR2?" or "How much has X in YEAR1 decreased in percentage with reference to YEAR2?" or "Is the value of X greater in YEAR1 or YEAR2? YEAR1 / YEAR2". Use different variations of these examples.
As output, provide a Python dictionary that has the questions as keys and the extracted values are the values of the dictionary. Do not write anything else. Do not provide any Markdown formatting.

Table: {}
Topics: {}
"""

df = pd.read_csv("annotation/data.tsv", sep="\t")

with open("json_config/en_queries_extended.json", 'r') as file:
    data = json.load(file)

messages = [
    [
        "system",
        "You are a helpful assistant that assists people in generating question answer pairs. You never generate question answer pairs that are not known based on the context or that are false.",
    ],
    [
        "human",
        ""
    ],
]
#ai_msg = llm.invoke(messages)

for i, row in df.iterrows():
    message_dp = deepcopy(prompt)

    gri = str(row["GRI"])
    page_nbr = str(row["page"])
    pdf_name = str(row["pdf_name"])
    table_nbr = str(row["nr_table_in_page"])

    print(f"annotation/{pdf_name.split('.')[0].strip()}/{page_nbr}_{table_nbr}.csv")
    file_name = f"annotation/{pdf_name.split('.')[0].strip()}/{page_nbr}_{table_nbr}.csv"
    try:
        table = pd.read_csv(file_name, header=None, sep=";", quoting=csv.QUOTE_NONE, escapechar='\\').to_html(index=False)
    except:
        print(f"Error with annotation/{pdf_name.split('.')[0].strip()}/{page_nbr}_{table_nbr}.csv")
        continue

    indicator_values = [v for k,v in data.items() if gri == k.split("-")[0]]
    indicator_values = '; '.join(indicator_values)

    message_dp = message_dp.format(table, indicator_values)

    messages[1][1] = message_dp

    #print(messages)

    ai_msg = llm.invoke(messages)

    try:
        dict_values = ast.literal_eval(ai_msg.content)
    except:
        print(f"Malformed node for annotation/{pdf_name.split('.')[0].strip()}/{page_nbr}_{table_nbr}.csv")
        continue

    for k,v in dict_values.items():
        new_dataset.append([pdf_name, gri, page_nbr, table_nbr, k, v])
    #print(new_dataset)

new_df = pd.DataFrame(new_dataset)
new_df.to_csv("qa_dataset_aggr.csv", sep=";")



