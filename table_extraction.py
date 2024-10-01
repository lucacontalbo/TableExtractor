import os
from unstructured.partition.pdf import partition_pdf
from tqdm import tqdm
from PyPDF2 import PdfReader, PdfWriter
from functools import lru_cache
from transformers import AutoModelForObjectDetection, AutoImageProcessor
import pytesseract
import pandas as pd

from PIL import Image
import torch

class TableTransformerTableExtractor:
    def __init__(self, model_name):
        self.model_name = model_name #"microsoft/table-transformer-detection"
        self.model = AutoModelForObjectDetection.from_pretrained(model_name)
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

    def extract_text_from_cell(self, image, box):
        cropped_image = image.crop((box[0], box[1], box[2], box[3]))
        text = pytesseract.image_to_string(cropped_image, config='--psm 6')  # PSM 6 for single block of text
        return text.strip()

    def organize_cells_into_grid(boxes, texts):
        rows = []
        current_row = []
        sorted_boxes = sorted(zip(boxes, texts), key=lambda x: x[0][1])  # Sort by y1 coordinate

        for i, (box, text) in enumerate(sorted_boxes):
            if current_row and abs(current_row[-1][0][1] - box[1]) > 10:  # New row detected
                rows.append(current_row)
                current_row = []
            current_row.append((box, text))
        if current_row:
            rows.append(current_row)

        return rows

    def process_image(self, img_file):
        image = Image.open(img_file)

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = inputs.to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        boxes = outputs.logits.argmax(-1).squeeze().cpu().numpy()
        table_data = []

        for box in boxes:
            text = extract_text_from_cell(image, box)
            table_data.append(text)

        table_grid = organize_cells_into_grid(boxes, table_data)
        df = pd.DataFrame([[cell[1] for cell in row] for row in table_grid])

        # Write the DataFrame to a CSV file
        csv_filename = "extracted_table.csv"
        df.to_csv(csv_filename, index=False, header=False)


class UnstructuredTableExtractor:
    def __init__(self, model_name, strategy):
        self.model_name = model_name #"yolo-x"
        self.strategy = strategy # "hi-res"

    @lru_cache
    def cached_partition_pdf(self, filename, strategy, model_name):
        return partition_pdf(
            filename=filename,
            strategy=strategy,
            infer_table_structure=True,
            model_name=model_name,
            languages=["eng"],
        )

    def extract_page(self, pdf_path, page_num):
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])  # Page number adjustment

        output_pdf_path = f"temp_page_{page_num}.pdf"
        with open(output_pdf_path, "wb") as f:
            writer.write(f)

        return output_pdf_path

    def extract_table_unstructured(self, documents):
        tables = []

        for doc_index, doc in tqdm(enumerate(documents)):
            pdf_name = doc.metadata["source"]

            page = doc.metadata["page"]

            #temp_pdf_path = self.extract_page(f"{pdf_name}", int(page))
            try:
                temp_pdf_path = self.extract_page(f"{pdf_name}", int(page))
            except:
                print(f"Error extracting page {page} from {pdf_name}")
                continue

            elements = self.cached_partition_pdf(
                filename=temp_pdf_path,
                strategy=self.strategy,
                model_name=self.model_name
            )

            tables_in_page = 0
            for element in elements:
                if element.category == "Table":
                    tables.append((element, pdf_name, page, tables_in_page))
                    tables_in_page+=1

            os.remove(temp_pdf_path)

        return tables
