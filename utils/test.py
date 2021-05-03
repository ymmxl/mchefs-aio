import json
from bs4 import BeautifulSoup as bs

t = json.load(open("p.json","r"))["content"]

soup = bs(t,"html.parser")
# print(soup.find({"div":"data-product-variation-info-json"}))
# print(soup.find_all({"attr":"data-product-variation-info-json"}))
print(soup.find(attrs={"data-product-variation-info":"314208313404"}).attrs["data-product-variation-info-json"])