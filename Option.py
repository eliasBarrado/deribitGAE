from datetime import datetime, timezone

class Option:
	def __init__(self, instrument_name):

		self.instrument_name = instrument_name

		l = instrument_name.split('-')

		self.symbol = l[0]
		self.date   = datetime.strptime(l[1],'%d%b%y')
		self.date   = self.date.replace(hour=8, tzinfo=timezone.utc)
		self.strike = int(l[2])
		self.side   = l[3]


	def get_date(self):
		return self.date

	def get_strike(self):
		return self.strike

	def get_instrument_name(self):
		return self.instrument_name


