from InfoScreen import InfoScreen

display = InfoScreen()
res = display.assemble_basic_screen()

print(display.get_calendar())
display.draw(*res)
