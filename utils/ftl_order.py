import requests,time

class Order:
	def __init__(self,order_number):
		self.order_number = order_number
	
	def check_order(self,order):
		shipped = False
		error = None
		r=""
		item = {
		"name":"",
		"order_number":order,
		"image":"",
		"sku":"",
		"tracking":"",
		"tracking_status":"",
		"carrier":""
		}
		s = requests.session()
		main_url = "https://footlocker.narvar.com/footlocker/tracking/startrack?order_number={}".format(order)
		order_url = "https://footlocker.narvar.com/tracking/itemvisibility/v1/footlocker/orders/{}".format(order)	
		s.headers.update({
		"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"accept-encoding":"gzip, deflate, br",
		"accept-language":"en-GB,en-US;q=0.9,en;q=0.8",
		"sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
		"sec-ch-ua-mobile": "?0",
		"upgrade-insecure-requests": "1",
		"referer":"https://footlocker.narvar.com/footlocker/tracking/startrack?order_number={}".format(order),
		"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
		})
		s.get(main_url)
		q = s.get(order_url)
		if r.status_code == 200:
			try:
				r = q.json()
			except Exception as e:
				if "error" in r.text:
					print("200: error page found")
				print("Failed getting json.")
				print(e)
		elif r.status_code == 403:
			print(r.request.headers)
			print(s.cookies)
			print(r.text)
			error = "Access denied/ rate limited."
			print(error)
		else:
			print(r.status_code)
			print("Failed fetching api")
			print(r.text)
			error = r.text
		if r:
			status = r.get("status")
			if status == "SUCCESS":
				for i in r["order_info"]["order_items"]:
					if i["fulfillment_status"] == "SHIPPED":
						print("Order: {} shipped!".format(order))
						item["name"] = i["name"]
						item["image"] = "https:"+i["item_image"]
						item["sku"] = i["sku"]
					else:
						print("Order: {} not shipped yet".format(order))
						break
				# if r.get("tracking_info"):
					for i in r["tracking_info"]:
						try:
							if i["carrier_name"] is not None:
								item["carrier"] = i["carrier_name"]
							else:
								item["carrier"] = r["order_info"]["shipments"][0]["carrier"]
						except Exception as e:
							print("Failed getting carrier info")
							print(e)
						try:
							if i["tracking_url"] is not None:
								item["tracking"] = i["tracking_url"]
							else:
								item["tracking"] = r["order_info"]["shipments"][0]["tracking_number"]
						except Exception as e:
							print("Failed getting tracking info")
							print(e)
						if item["carrier"] = "armx":
							item["tracking"] = "https://www.aramex.com/track/results?ShipmentNumber={}".format(item["tracking"])
						item["tracking_status"] = i["status"]
					if item["name"] and item["image"] and item["sku"] and item["tracking"]:
						shipped = True
			elif status == "FAILURE":
				error = "No orders/ghosted."
				print(error)
				print(r["messages"])
		# error but not not shipped = failed to fetch
		# no error and not shipped = 
		# no error and shipped = 
		return error,shipped,item

	def process(self):
		tmp = []
		for i in self.order_number:
			error,is_shipped,item = self.check_order(i)
			tmp.append([error,is_shipped,item])
			time.sleep(10)
		return tmp
			


if __name__ == "__main__":
	n = ["xxx","xxx"]
	t = Order(n)
	q = t.process()
	for i in q:
		if not i[0]:
			if i[1]:
				print(i[2])