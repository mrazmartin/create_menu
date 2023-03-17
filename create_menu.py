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
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, PageBreak, PageTemplate
from reportlab.lib.styles import ParagraphStyle


TOP_MARGIN = 20
SIDE_MARGIN = 20

class create_menu():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.segments = defaultdict(lambda: [])
        self.num_segments = 0
        self.num_items = 0
        self.dims = A4
    
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
    def __init__(self, name_str, menu: create_menu) -> None:
        # A4 size = 210 x 297 mm
        self.dims = A4
        self.pdf_doc = canvas.Canvas(name_str+"_menu.pdf", pagesize=self.dims, bottomup=1)
        self.width, self.height = self.pdf_doc._pagesize
        self.handle_logo()

        self.pdf_doc.setLineWidth(.3)
        self.set_font(menu)
        #   self.pdf_doc.drawString(10, 10, 'Hello, World!')
        message = self.create_message(menu)
        self.draw_paragraph(message, 50, self.dims[1]-self.logo_height-TOP_MARGIN, 350, 350)
        self.pdf_doc.save()

    def create_message(self, menu: create_menu):
        message = ""
        for i in menu.segments:
            message = message + "\n<font color='blue'>"+ i + "</font>\n\n"
            for item in menu.segments[i]:
                num_dots = self.calc_dots(item.name, item.price)
                new_part = item.name + " " + num_dots*"." + " " + item.price
                print(self.pdf_doc.stringWidth(new_part, self.pdf_doc._fontname, self.pdf_doc._fontsize))
                message = "<font color='black'>" + message + new_part + "</font>\n"
        return message

    def calc_dots(self, name, price) -> int:
        name_len = self.pdf_doc.stringWidth(name, self.pdf_doc._fontname, self.pdf_doc._fontsize)
        price_len = self.pdf_doc.stringWidth(price, self.pdf_doc._fontname, self.pdf_doc._fontsize)
        dot_len = self.pdf_doc.stringWidth(".", self.pdf_doc._fontname, self.pdf_doc._fontsize)
        num_dots = int((self.dims[0]/2 - (name_len + price_len)) / int(dot_len) )
        print(f"name len: {int(name_len)}    price len: {int(price_len)}  dot len: {int(dot_len)}   num_dots: {num_dots}")
        return num_dots
    
    def draw_paragraph(self, msg, x, y, max_width, max_height):
        message_style = ParagraphStyle('Normal')
        message = msg.replace('\n', '<br />')
        message = Paragraph(message, style=message_style)
        w, h = message.wrap(max_width, max_height)
        message.drawOn(self.pdf_doc, x, y - h)

    def set_font(self, menu: create_menu):
        font_size = (self.dims[1] - 2*self.logo_height) // (menu.num_items + menu.num_segments*0.6)
        pdfmetrics.registerFont(TTFont('Bahn', 'BAHNSCHRIFT.ttf'))
        self.pdf_doc.setFont('Bahn', font_size)

    def handle_logo(self):
        try:
            self.logo = ImageReader("logo.png")
        except Exception as e:
            print("Could not open the logo image: ", e)
            exit(1)
        image_width, image_height = self.logo.getSize()
        
        scale = self.dims[0] / (2*image_width + 2*SIDE_MARGIN) 
        self.logo_width = image_width * 0.9*scale
        self.logo_height = image_height * 0.9*scale
        x1 = (self.dims[0] - 2*self.logo_width)/ 2 - SIDE_MARGIN
        x2 = (self.dims[0] - 2*self.logo_width)/ 2  + self.dims[0]/2 - SIDE_MARGIN
        y1 = (self.dims[1] - self.logo_height) - TOP_MARGIN
        y2 = (self.logo_height) - TOP_MARGIN
        self.pdf_doc.drawImage("logo.png", x1, y1, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x2, y1, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x1, y2, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x2, y2, width=self.logo_width, height=self.logo_height)


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
    
    menu_pdf("vivo", menu)


if __name__ == "__main__":
    main()