#The primary function of this module is to stream exchange data from a database 
#into another module. There are two ways to do that:
#	1) Simulate sending out data as a fraction of real time (1 minute = 1 second real time)
#	2) Send all data as fast as possible
#
#	Kee in mind, this simulator does not allow the selection of different products
#	it uses whatever data is in the database
#
#	I may add ways of stepping through data later on if I find it useful
#	
import threading, queue
from pymongo import MongoClient
from datetime import datetime
import time

class DataStream(threading.Thread):
	def __init__(self,real_time = True):
		super().__init__()
		
		self.stop_request = threading.Event()
		self._data_queue = queue.Queue()
		
		self._sleep_time = 0
		if real_time:
			self._sleep_time = 1
	
	def run(self):
		client = MongoClient()
		db = client.profitdb
		
		exch_data = db.exch_data.find()
		

		for field in exch_data:
			if self.stop_request.isSet():
				return
		
			field['time'] = datetime.utcnow().isoformat() + 'Z' #have to trick data manager into thinking this data is current
			self._data_queue.put(field)
			time.sleep(1)

	
	def close(self, timeout=None):
		self.stop_request.set()
		super().join(timeout)
		
	def getStream(self):
		return self._data_queue
		
		
		