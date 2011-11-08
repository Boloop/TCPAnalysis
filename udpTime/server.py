

import UDPTime


s = UDPTime.Server(3344)
s.bind()
s.start()

while 1:
	a = raw_input( "Press q to quit:")
	if a == "q":
		s.die()
		break

s.join()

