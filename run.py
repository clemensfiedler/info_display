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

try:
    refresh = 60*int(vargs['refresh'])
except:
    refresh = 60*10

try:
    time_end = 3600*int(vargs['time'])
except:
    time_end = 3600*24


# start service
display = InfoScreen()

print('starting service\nrefresh every {} m\nstops in {} h'.format(refresh//60, time_end//3600))

display.start_service(refresh=refresh, time_end=time_end)
