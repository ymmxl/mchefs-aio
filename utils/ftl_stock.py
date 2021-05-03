import requests,json

class Check:
	def __init__(self,sku):
		self.sku = sku
		self.complete = False
		self.error = None
		self.s = requests.session()

	def get_stock(self):
		stock = False
		self.headers.update({
		"upgrade-insecure-requests":"1",
		"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
		"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"accept-encoding":"gzip, deflate, br",
		"accept-language":"en-GB,en-US;q=0.9,en;q=0.8"
			})
		url = "https://www.footlocker.sg/INTERSHOP/web/FLE/FootlockerAsiaPacific-Footlocker_SG-Site/en_GB/-/SGD/ViewProduct-ProductVariationSelect?BaseSKU={}&InventoryServerity=ProductDetail".format(self.sku)
		r = s.get(url)
		if r.status_code == 200:
			if "Sold Out!" r.text:
				print("{}: OOS page is up".format(sku))
			elif "\"content\"" in r.text:
				stock = json.loads(r.text)["content"]
		else:
			print(r.status_code)
			print(r.text)
		return stock

if __name__ == "__main__":
	sku = "314208313404"
	y = Check(sku)
	y.get_stock()