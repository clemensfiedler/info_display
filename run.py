from InfoScreen import InfoScreen

display = InfoScreen()
display.start_service(refresh=60*10, time_end=3600*24)


# res = display.assemble_basic_screen()

# display.draw(*res)
