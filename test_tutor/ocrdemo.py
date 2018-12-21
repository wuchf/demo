from pyocr import pyocr
from PIL import Image
tools = pyocr.get_available_tools()[:]
if len(tools) == 0:
    print("No OCR tool found")
print("Using '%s'" % (tools[0].get_name()))
print (tools[0].image_to_string(Image.open('D:\\ans\\0.png'),lang='eng'))
print (tools[0].image_to_string(Image.open('D:\\ans\\zuoti-answer2.png'),lang='chi_sim'))