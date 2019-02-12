from InfoScreen import InfoScreen

display = InfoScreen(test=True)
# display.start_service(refresh=1, time_end=5)

res = display.assemble_basic_screen()
cal = display.get_calendar()
display.draw_test(*res)



