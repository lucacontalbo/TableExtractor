import os
from unstructured.partition.pdf import partition_pdf
from tqdm import tqdm
from PyPDF2 import PdfReader, PdfWriter
from functools import lru_cache


class UnstructuredTableExtractor:
    def __init__(self, model_name, strategy):
        self.model_name = model_name
        self.strategy = strategy

    @lru_cache
    def cached_partition_pdf(self, filename, strategy, model_name):
        return partition_pdf(
            filename=filename,
            strategy=strategy,
            infer_table_structure=True,
            model_name=model_name
        )

    def extract_page(self, pdf_path, page_num):
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num - 1])  # Page number adjustment

        output_pdf_path = f"temp_page_{page_num}.pdf"
        with open(output_pdf_path, "wb") as f:
            writer.write(f)

        return output_pdf_path

    def extract_table_unstructured(self, documents):
        for i,doc in tqdm(documents.iterrows()):
            pdf_name = row["Nome PDF"].iloc[0]

            page = row["Valore"]["Pagina"]
            value = str(row["Valore"]["Valore testuale"])

            try:
                temp_pdf_path = extract_page(f"../pdfs/{pdf_name}", int(page))
            except:
                print(f"Error extracting page {page} from {pdf_name}")
                continue

            elements = cached_partition_pdf(
                filename=temp_pdf_path,
                strategy=self.strategy,
                model_name=self.model_name
            )

            tables = []
            for element in elements:
                if element.category == "Table":
                    tables.append(element)

        os.remove(temp_pdf_path)

        return tables