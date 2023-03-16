# created by Big Chonga Martin Mráz

from collections import defaultdict
import sys
import os
import chardet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

TOP_MARGIN = 20
SIDE_MARGIN = 20

class create_menu():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.segments = defaultdict(lambda: [])
        self.num_segments = 0
        self.num_items = 0
    
    def read_file(self):
        rawdata = open(self.file_path, 'rb').read()
        result = chardet.detect(rawdata)
        
        if result['encoding'] != "utf-8":
            print("WRONG FILE ENCODING")
            exit(1)
        
        f = open(self.file_path, "r", encoding='utf-8')
        last_segment = ""
        for line in f:
            if not line.startswith(" "):
                self.segments[line.strip()]
                last_segment = line.strip()
                self.num_segments += 1
            else:
                self.segments[last_segment].append(food_item(line))
                self.num_items += 1
        self.segments[" "] = self.segments.pop("##")


class menu_pdf():
    def __init__(self, name_str) -> None:
        # A4 size = 210 x 297 mm
        self.pdf_doc = canvas.Canvas(name_str+"_menu.pdf", pagesize=A4, bottomup=1)
        self.width, self.height = self.pdf_doc._pagesize
        self.handle_logo()

        self.pdf_doc.setLineWidth(.3)
        self.set_font()
        self.pdf_doc.setFont('Bahn', 12)
        self.pdf_doc.drawString(10, 10, 'Hello, World!')
        self.pdf_doc.save()
    
    def set_font(self):
        pdfmetrics.registerFont(TTFont('Bahn', 'BAHNSCHRIFT.ttf'))

    def handle_logo(self):
        try:
            self.logo = ImageReader("logo.png")
        except Exception as e:
            print("Could not open the logo image: ", e)
            exit(1)
        image_width, image_height = self.logo.getSize()
        
        scale = A4[0] / (2 * image_width + 2 * SIDE_MARGIN) 
        logo_width = image_width * scale * 0.9
        logo_height = image_height * scale * 0.9
        x1 = (A4[0] - 2*logo_width) / 2 - SIDE_MARGIN
        x2 = (A4[0] - 2*logo_width) / 2  + A4[0]/2 - SIDE_MARGIN
        y = (A4[1] - logo_height) - TOP_MARGIN
        self.pdf_doc.drawImage("logo.png", x1, y, width=logo_width, height=logo_height)
        self.pdf_doc.drawImage("logo.png", x2, y, width=logo_width, height=logo_height)


class food_item():
    def __init__(self, line) -> None:
        self.line = line
        self.name = ""
        self.price = ""
        self.get_name()
        self.size = len(self.name) + len(self.price) 

    def get_name(self):
        self.name, self.price = self.line.split('€')
        self.name = self.name.strip()
        self.price = self.price.strip()

def main():
    menu_path = "menu.txt"
    if len(sys.argv) != 2:
        if not len(menu_path):
            print(f"Usage: python3 {sys.argv[0]} <menu_datapath>")
    else:
        menu_path = sys.argv[1]  
    menu = create_menu(menu_path)
    menu.read_file()
    for i in menu.segments:
        print(i)
        for item in menu.segments[i]:
            print(repr(item.name), repr(item.price))
    menu_pdf("vivo")


if __name__ == "__main__":
    main()