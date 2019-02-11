from InfoScreen import InfoScreen

display = InfoScreen()
display.start_service(refresh=60*5, time_end=60*5*20)


# res = display.assemble_basic_screen()

# display.draw(*res)
