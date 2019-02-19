from InfoScreen import InfoScreen
from argparse import ArgumentParser


# paste arguments
parser = ArgumentParser()
parser.add_argument("-r", "--refresh", dest="refresh",
                    help="refresh time in minutes")
parser.add_argument("-t", "--time", dest="time_end",
                    help="runtime in hours")

args = parser.parse_args()
vargs = vars(args)

# run code
display = InfoScreen(test=True)

res = display.assemble_basic_screen()
# wet = display.get_weather()
display.draw_test(*res)



