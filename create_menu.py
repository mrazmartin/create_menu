# created by Big Chonga Martin Mráz

from collections import defaultdict
import sys
import math
import chardet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet

TOP_MARGIN = 20
LOGO_SIDE_MARGIN = 40
TEXT_SIDE_MARGIN = 20
SET_FONT_SIZE = False
MAX_FONT = 14

TERMINAL_PRINT = False
MAX_LINE_SCALE = 30

class food_item():
    def __init__(self, line) -> None:
        self.line = line
        self.name = ""
        self.price = ""
        self.get_name()
        self.name_len = 0
        self.price_len = 0
        self.size = len(self.name) + len(self.price) 

    def get_name(self):
        self.name, self.price = self.line.split('€')
        self.name = self.name.strip().upper()
        self.price = self.price.strip()

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
        self.max_line_len = 0
        for line in f:
            if not line.startswith(" "):
                self.segments[line.strip()]
                last_segment = line.strip()
                self.num_segments += 1
                self.max_line_len = max(self.max_line_len, len(last_segment))
            else:
                self.segments[last_segment].append(food_item(line))
                self.num_items += 1
                self.max_line_len = max(self.max_line_len, self.segments[last_segment][-1].size)
        self.segments[" "] = self.segments.pop("##")



class menu_pdf():
    def __init__(self, name_str, menu: create_menu) -> None:
        # A4 size = 210 x 297 mm
        self.dims = A4
        self.pdf_doc = canvas.Canvas(name_str+"_menu.pdf", pagesize=self.dims, bottomup=1)
        self.width, self.height = self.pdf_doc._pagesize
        self.handle_logo()

        self.pdf_doc.setLineWidth(.3)
        self.set_font(menu, msg_ret = False)
        #   self.pdf_doc.drawString(10, 10, 'Hello, World!')
        message = self.create_message(menu)
        #                            distance from left edge    distance from top edge
        self.draw_paragraph(message, x=TEXT_SIDE_MARGIN, y=self.dims[1]-self.logo_height-TOP_MARGIN,
                            max_width=A4[0]/2, max_height=100, menu=menu)
        self.pdf_doc.save()

    def create_message(self, menu: create_menu):
        message = ""
        for i in menu.segments:
            message = message + "\n<font color='0.58, 0.54, 0.33'>"+ i + "</font>\n"
            for item in menu.segments[i]:
                num_dots = self.calc_dots(item)
                new_part = item.name + " " + num_dots*"." + " " + item.price
                if TERMINAL_PRINT:
                    print(self.pdf_doc.stringWidth(new_part, self.pdf_doc._fontname, self.pdf_doc._fontsize))
                message = "<font color='black'>" + message + new_part + "</font>\n"
        return message

    def calc_dots(self, item: food_item) -> int:
        item.name_len = self.pdf_doc.stringWidth(item.name, self.pdf_doc._fontname, self.pdf_doc._fontsize)
        item.price_len = self.pdf_doc.stringWidth(item.price, self.pdf_doc._fontname, self.pdf_doc._fontsize)
        dot_len = self.pdf_doc.stringWidth(".", self.pdf_doc._fontname, self.pdf_doc._fontsize)
        num_dots = int((self.dims[0]/2 - (item.name_len + item.price_len)-2*TEXT_SIDE_MARGIN) / dot_len )

        if TERMINAL_PRINT:
            print(f"\n{item.name} - {item.price}\nname len: {int(item.name_len)}",
                    f"price len: {int(item.price_len)}",
                f"dot len: {int(dot_len)}   num_dots: {num_dots}")
        return num_dots
    
    def draw_paragraph(self, msg, x, y, max_width, max_height, menu):
        styles = getSampleStyleSheet()
        font_atributes = self.set_font(menu)
        message_style = ParagraphStyle(name='Default', parent=styles['Normal'], leading = font_atributes[0],
                                       fontSize=font_atributes[0], fontStyle=font_atributes[1], 
                                       maxSize = (max_width, max_height))
        message = msg.replace('\n', '<br />')
        message = Paragraph(message, style=message_style)
        w, h = message.wrap(max_width, max_height)
        message.drawOn(self.pdf_doc, x, y - h)

    def set_font(self, menu: create_menu, msg_ret = True):
        pdfmetrics.registerFont(TTFont('Bahn', 'BAHNSCHRIFT.ttf'))
        #self.pdf_doc.setFont('Bahn', font_size)
        if SET_FONT_SIZE:
            font_size = 14
        else:
            font_size = (self.dims[1] - 2*self.logo_height -2*TOP_MARGIN) / (menu.num_items + menu.num_segments*2.2)
            font_size = min(font_size, MAX_FONT)
            print(f"font size set to: {font_size}")

        if menu.max_line_len/MAX_LINE_SCALE > 1:
            font_size = font_size * math.sqrt(MAX_LINE_SCALE/menu.max_line_len)

        self.pdf_doc.setFontSize(font_size)
        if msg_ret:
            return font_size, "Bahn"

    def handle_logo(self):
        try:
            self.logo = ImageReader("logo.png")
        except Exception as e:
            print("Could not open the logo image: ", e)
            exit(1)
        image_width, image_height = self.logo.getSize()
        
        scale = self.dims[0] / (2*image_width + 2*LOGO_SIDE_MARGIN) 
        self.logo_width = image_width * 0.9*scale
        self.logo_height = image_height * 0.9*scale
        x1 = (self.dims[0] - 2*self.logo_width)/ 2 - LOGO_SIDE_MARGIN
        x2 = (self.dims[0] - 2*self.logo_width)/ 2  + self.dims[0]/2 - LOGO_SIDE_MARGIN
        y1 = (self.dims[1] - self.logo_height) - TOP_MARGIN
        y2 = (self.logo_height) - TOP_MARGIN
        self.pdf_doc.drawImage("logo.png", x1, y1, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x2, y1, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x1, y2, width=self.logo_width, height=self.logo_height)
        self.pdf_doc.drawImage("logo.png", x2, y2, width=self.logo_width, height=self.logo_height)


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