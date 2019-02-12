from InfoScreen import InfoScreen

display = InfoScreen(test=True)
# display.start_service(refresh=1, time_end=5)

res = display.assemble_basic_screen()
# wet = display.get_weather()
display.draw_test(*res)



