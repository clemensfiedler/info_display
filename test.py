from InfoScreen import InfoScreen

display = InfoScreen(test=True)
res = display.assemble_basic_screen()

print(display.get_calendar())
display.draw_test(*res)



