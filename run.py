from InfoScreen import InfoScreen

display = InfoScreen()
res = display.assemble_basic_screen()
display.draw_test(*res)


#     if (loop.time() + 1.0) < end_time:
#         loop.call_later(44, display_basic_screen, end_time, loop)
#
#     else:
#         epd.Clear(0xFF)
#         loop.stop()
#
# def turn_off():
#     epd.Clear(0xFF)
#     epd.sleep()

# # start event loop
# loop = asyncio.get_event_loop()
# end_time = loop.time() + 600.0
# loop.call_soon(display_basic_screen, end_time, loop)
#
# try:
#     loop.run_forever()
# finally:
#     loop.close()

