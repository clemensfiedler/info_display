from InfoScreen import InfoScreen

display = InfoScreen()
res = display.assemble_basic_screen()

display.draw(*res)
