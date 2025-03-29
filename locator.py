import os
import subprocess
import logging
import sys

class Locator:
	def __init__(self, logger : logging.Logger):
		self.logger = logger
		self.cmd = 'lolcate' if self.has_lolcate() else None
		# self.limit = 5
		self.opt = ''

	# def set_limit(self, limit : int) -> None:
	# 	self.logger.debug('set limit to '+str(limit))
	# 	self.limit = limit

	# def set_locate_opt(self, opt):
	# 	print('set locate opt to '+opt)
	# 	self.opt = opt

	def has_lolcate(self) -> bool:
		try:
			subprocess.check_call(['which', 'lolcate'])
			return True
		except:
			return False

	def run(self, pattern) -> list[str]:
		if self.cmd == None:
			raise RuntimeError('command lolcate not found or options config error')
		else:
			cmd = [self.cmd]
			args = pattern.split(' ')
			# if args[0] == 'r':
			# 	cmd.extend(args[1:])
			# else:
			# 	cmd.append(self.opt)
			cmd.extend(args)
			self.logger.debug(f"executing {cmd}")
			output = subprocess.check_output(cmd).decode('utf-8')
			split = output.splitlines()
			# self.logger.debug(f"{split}")
			count = len(split)
			self.logger.debug(f"found {count} matches")
			return split
