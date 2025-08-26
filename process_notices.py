import requests
from fpdf import FPDF
import tempfile
import os
from PIL import Image
from pdf2image import convert_from_path

from pathlib import Path
from typing import Literal
from datetime import datetime
from pydantic import BaseModel
from ollama import Client


class summarize():
    def __init__(self):
        self.default_dpi = 300
        self.tesseract_lang = "eng"

    def download(self, url, pdf_name="/home/vector/project/github/ping/testing_new.pdf"):
        try:
            with requests.Session() as session:
                notifications_url = 'https://www.imsnsit.org/imsnsit/notifications.php'
                session.get(notifications_url, verify=False)

                file_response = session.get(
                    url,
                    allow_redirects=True,
                    verify=False,
                    headers={
                        'Referer': notifications_url,
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/91.0.4472.124 Safari/537.36'
                    }
                )

                if file_response.status_code == 200:
                    content_type = file_response.headers.get('Content-Type', '')
                    if 'application/pdf' in content_type:
                        with open(pdf_name, 'wb') as file:
                            file.write(file_response.content)
                    elif content_type.startswith('image/'):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".img") as tmp:
                            tmp.write(file_response.content)
                            tmp_path = tmp.name
                        img = Image.open(tmp_path).convert("RGB")
                        img.save(pdf_name, "PDF", resolution=self.default_dpi)
                        os.unlink(tmp_path)
                    else:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, file_response.text)
                        pdf.output(pdf_name)
                else:
                    raise RuntimeError(f"Failed to download: HTTP {file_response.status_code}")
        except Exception as e:
            print(f"An error occurred in download(): {e}")
            raise
        return pdf_name

    def ocr(self, path):
        # Define the schema for image objects
        class Object(BaseModel):
            name: str
            confidence: float
            attributes: str

        class ImageDescription(BaseModel):
            text: str
            summary: str
            tags: Literal['Fee submition', 'Datesheet', 'Misc.']
            time_of_day: datetime | None
            department: Literal[
                'ECE', 'Admin', 'CSE', 'IT', 'Mechanical',
                'Electrical', 'Management', 'BBA', 'MBA',
                'PhD', 'Others'
            ]
            # priority: int | None = None

        client = Client(host='http://192.168.1.10:11434')
        # client = Client(host='http://localhost:11434')
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        results = []
        # Convert PDF pages to images
        images = convert_from_path(str(path), dpi=self.default_dpi)
        for idx, img in enumerate(images):
            temp_img = f"/tmp/page_{idx+1}.png"
            img.save(temp_img, "PNG")

            response = client.chat(
                model='gemma3:4b',
                format=ImageDescription.model_json_schema(),
                messages=[
                    {
                        'role': 'user',
                        'content': (
                            "Extract information from this image and fill the JSON according to the schema. "
                            "Fields: text, summary, tags, time_of_day, department, priority. "
                            "If unknown, leave empty or null. Return only valid JSON. "
                            "Keep summary TO THE POINT and professional."
                        ),
                        'images': [temp_img],
                    },
                ],
                options={'temperature': 0},
            )

            # Validate response into schema
            image_analysis = ImageDescription.model_validate_json(response['message']['content'])
            results.append(image_analysis.model_dump())

        return results

    def update(self, json):
        
        return

    def main(self, url):
        path = self.download(url)
        text = self.ocr(path)
        print(text)
        return text


if __name__ == "__main__":
    obj = summarize()
    # random notice for testing
    url = "https://www.imsnsit.org/imsnsit/plum_url.php?FJNYX2ih5DxC8pqvm/t0GpkRiKPeHuIBhSThO1O/cut3m+JjuXTfNhpKXp87gmCasSAVwp74QbHVXbrK3VLBb/B4alLAlzBZq5ukb1jK0npafDcai/jUZEOoI5vYki4S51yZNQ3Mdu0OjRtls/OJGfs741ktHO2oAFhN2VaBcIOxt8m4cDThc2s7QAbDwI+MowYwXtNhct1jgmAzyiiqNxjZBgHu+MU9wA3AcnTOGW/4RX/Pf26YEOaZ7QHMcIAwmjt7k99AcfTTcn53ulzuwA=="
    obj.main(url)
