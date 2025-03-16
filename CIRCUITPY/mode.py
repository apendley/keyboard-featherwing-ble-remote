
class Mode:
	def __init__(self, device):
		self._device = device

	@property
	def device(self):
		return self._device

	def update(self):
		pass

	def enter(self):
		pass

	def exit(self):
		pass