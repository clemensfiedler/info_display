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
except None:
    refresh = 60*10

try:
    time_end = 3600*int(vargs['time_end'])
except None:
    time_end = 3600*24*30

# start service
display = InfoScreen()

print('starting service\n' + '-'*16)
print('refresh: {} minutes'.format(refresh//60))

if time_end < 0:
    print('runs indefinitely')
elif time_end>3600*2:
    print('stops : {} days'.format(time_end//(3600*24)))
else:
    print('stops : {} hours'.format(time_end//3600))

display.start_service(refresh=refresh, time_end=time_end)
