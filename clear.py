import epd7in5b

epd = epd7in5b.EPD()
epd.init()
epd.Clear(0xFF)

print('screen cleared')
