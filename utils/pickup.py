import re,sys,requests,json,pytz
from requests.exceptions import RequestException
from datetime import datetime as dt
class Pickup:
	def __init__(self,profile):
		self.profile = profile
		self.complete = False
		self.error = None
		self.s = requests.session()

	def get_page(self):
		self.s.headers.update({
		"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
		"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"accept-encoding":"gzip, deflate, br",
		"accept-language":"en-GB,en-US;q=0.9,en;q=0.8"		
			})
		try:
			r = self.s.get("https://mydhl.express.dhl/my/en/schedule-pickup.html")
		except RequestException as e:
			print("Error get_page: {}".format(e))
			return None
		return r
	
	def validate_format(self):
		v = False
		self.s.headers.update({
			"content-type":"application/json;charset=UTF-8",
			"referer":"https://mydhl.express.dhl/my/en/schedule-pickup.html",
			"origin":"https://mydhl.express.dhl"
			})
		payload = {
			"airWayBillNumber": re.sub(re.compile(r"\s+"),"",self.profile["awbill"])
		}
		#r = s.get("https://mydhl.express.dhl/api/shipment/pickup/details?airWayBillNumber={}&phoneNumber={}".format(AWBILL,t["phone"]))
		#print(r.status_code)
		try:
			r = self.s.post("https://mydhl.express.dhl/api/airwaybillnumber/validate",json = payload)
		except RequestException as e:
			print("Error validate_format: {}".format(e))
			return v
		if not r.status_code == 200:
			if "not valid" in r.text:
				print("awbill is not valid")
			else:
				print("wrong awbill submitted.")
				print(r2.text)
		else:
			if not r.text:
				print("awbill validated")
				v = True
			elif r.json().get("fieldErrors"):
				print(r.json()["fieldErrors"])
			else:
				print("Error parsing validate_awbill")
				print(r.text)
		return v

	def validate_awbill(self):
		v=False
		try:
			r = self.s.get("https://mydhl.express.dhl/api/shipment/pickup/standalone/verify/airwaybillnumber/{}".format(self.profile["awbill"]))
		except RequestException as e:
			print("Error validate_awbill: {}".format(e))
			return v
		if not r.status_code == 200:
			print(r.json()["errors"][0].split("error_")[1])
		else:
			v=True
		return v

	def validate_address(self):
		v=False
		try:
			r = self.s.get("https://mydhl.express.dhl/api/location/validate?city={}&countryCode=MY&postCode={}".format(self.profile["city"],self.profile["postcode"]))
		except RequestException as e:
			print("Error validate_address: {}".format(e))
			return v
		if r.status_code == 200:
			if not r.json()["postalLocationValidFlag"]:
				print("city and postcode does not match please try again")
			else:
				print("Address validated")
				v=r.json()
		elif r.status_code == 404:
			print("Wrong city or postcode")
		return v

	def validate_cutoff(self):
		v=None
		p = {
		"cityName":self.profile["city"],
		"zipCode":self.profile["postcode"],
		"citySuburbName":"",
		"countryCode":"MY",
		"airWayBillNumber":self.profile["awbill"],
		"pickCutoffDate":self.profile["date"]
		}
		try:
			r = self.s.post("https://mydhl.express.dhl/api/shipment/pickup/cutoff",json = p)
		except RequestException as e:
			print("Error validate_cutoff: {}".format(e))
			return v
		if r.status_code == 200:
			v = r.json()
		else:
			print("Error in validate_cutoff")
			print(r.status_code)
			print(r.text)
		return v

	def submit(self,f):
		f = json.dumps(f)
		self.s.headers.update({
			"accept": "application/json, text/plain, */*",
			"content-type":"application/json;charset=UTF-8",
			"accept-encoding": "gzip, deflate, br"
			})
		try:
			r = self.s.post("https://mydhl.express.dhl/api/shipment/pickup/standalone",data = f)
		except RequestException as e:
			print("Error submit: {}".format(e))
			return None
		return r

	def process(self):
		if not all(self.profile.get(i) for i in ["name","phone","email","eTime","awbill","date","add1","add2","city","postcode","state","package"]):
			self.error = "Incomplete profile"
			return self.complete,self.error
		with self.s:
			r1 = self.get_page()
			if not r1:
				self.error = "Error get_page"
				return self.complete,self.error
			v2 = self.validate_format()
			if not v2:
				self.error = "Error validate_format"
				return self.complete,self.error
			v3 = self.validate_awbill()
			if not v3:
				self.error = "Error validate_awbill"
				return self.complete,self.error		
			v4 = self.validate_address()
			if not v4:
				self.error = "Error validate_adress"
				return self.complete,self.error	
			countryDivisionCode = v4["countryDivisionCode"]	
			serviceAreaCode = v4["serviceAreaCode"]
			v5 = self.validate_cutoff()
			if not v5:
				self.error = "Error validate_cutoff"
				return self.complete,self.error				
			#serviceAreaCode = v5["serviceAreaCode"]
			package = int(self.profile["package"])
			weight = 1.5*package
			awbill = self.profile["awbill"]
			date = self.profile["date"]
			eTime = self.profile["eTime"]
			#Return the day of the week as an integer, where Monday is 0 and Sunday is 6
			b=pytz.timezone("singapore").localize(dt.strptime(date,"%Y-%m-%d")).weekday()
			if b == (5 or 6):
				lTime = "12:00"
			else:
				lTime = "16:30"
			name = self.profile["name"]
			phone = self.profile["phone"]
			email = self.profile["email"]
			add1 = self.profile["add1"]
			add2 = self.profile["add2"]
			city = self.profile["city"]
			postcode = self.profile["postcode"]
			state = self.profile["state"]

			f = {
			"pickupDetails": {
				"pickupLocationType": "pickup_reception",
				"pickupLocationOtherDescription": "",
				"instructions": "please call when you arrive thanks!",
				"pickupDate": date,
				"pickupWindow": {
					"earliestTime": eTime,
					"latestTime": lTime
				},
				"pickupLocation": {
					"name": name,
					"company": "",
					"contactKey": "00",
					"pickupAddress": {
						"countryCode": "MY",
						"addressLine1": add1,
						"addressLine2": add2,
						"addressLine3": None,
						"postCode": postcode,
						"cityName": city,
						"countryDivisionName": state,
						"countryDivisionCode": countryDivisionCode,
						"countryDivisionTypeCode": "S",
						"addressType": "RESIDENTIAL",
						"serviceAreaCode": serviceAreaCode,
						"citySuburbName": None,
						"streetNumber": None
					}
				},
				"email": email,
				"phoneDetails": {
					"phoneType": "MOBILE",
					"phoneCountryCode": "60",
					"phone": phone,
					"countryBanner": "MY",
					"smsEnabled": False
				},
				"phoneDetails2": None
			},
			"packageList": [],
			"numberOfPackages": package,
			"largestPackageDimensions": {
				"unit": "CM",
				"height": 35,
				"width": 25,
				"length": 15
			},
			"totalWeight": {
				"unit": "KG",
				"value": weight
			},
			"needCourier": False,
			"bookingReferenceNumber": None,
			"airWayBillNumber": awbill,
			"accountDetails": None
			}

			r6 = self.submit(f)
			if not r6:
				self.error = "Error submit"
				print("Error submit")
				return self.complete,self.error	
			elif r6.status_code == 200:
				print("Successfully scheduled\n{}".format(r6.text))
				self.complete = r6.text
				return self.complete,self.error


if __name__ == "__main__":
	process()
