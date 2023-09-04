"""
main executable
"""
import argparse
import yaml
import locale
from post_caldav_events.datetime import set_timezone, today, days
from post_caldav_events.input.form import update_events
from post_caldav_events.nextcloud.fetch import fetch_events
from post_caldav_events.output.message import message
from post_caldav_events.output.telegram import send_telegram, get_telegram_updates
from post_caldav_events.output.umap import createMapData
from post_caldav_events.output.newsletter import send_newsletter

# Get Arguments from Commandline 
def get_args ():
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='path to config file, defaults to config.yml')
    argparser.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0/None means today')
    argparser.add_argument("-qe", "--query-end", dest='query_end', type=int, help='number of days to query events from CalDav server, starting from query-start')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    argparser.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    argparser.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    argparser.add_argument("-n", "--newsletter", dest='send_newsletter', help='send email-newsletter', action='store_true')
    argparser.add_argument("-r", "--recipients", dest='recipient', help='override newsletter recipients from config - useful for testing')
    argparser.add_argument("-p", "--print", dest='print', help='print message to stdout', action='store_true')
    argparser.add_argument("-t", "--telegram", dest='send_telegram', help='send message to telegram', action='store_true')
    argparser.add_argument("-tid", "--telegram-id", dest='telegram_id', help='override telegram_id from config - useful if you have a channel for testing and one for production')
    argparser.set_defaults(config_file="config.yml", query_start=1, query_end=1, telegram_id=None)
    args = argparser.parse_args()
    return args

# Main Function if run as standalone program
def main(events = {}):
    args = get_args() # get Arguments from CLI
    try: # get Config from YAML file
        with open(args.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Config File not Found"); exit() 
    locale.setlocale(locale.LC_TIME, config['format']['time_locale']) #set time locale
    set_timezone(config) # set timezone
    if args.get_telegram_updates: # get id from telegram group/channel
        print(get_telegram_updates(config)); exit()
    if args.update_events: # update events from Form Mails
        update_events(config)
    querystart = today() + days(args.query_start); queryend = querystart + days(args.query_end) # prepare query from nextcloud with args from cli
    events = fetch_events(config, querystart, queryend) # get events from nextcloud
    if args.update_map:
        createMapData(events) # update the umap
    if args.print:
        print(message(config, events, querystart, queryend, mode='plain')) # print message to stdout
    if args.send_newsletter:
        recipient = args.recipient if args.recipient is not None else None
        send_newsletter(config, querystart, queryend, events, recipient) # send mail newsletter
    if args.send_telegram:
        telegram_id = config['telegram']['group_id'] if args.telegram_id is None else args.telegram_id 
        send_telegram(config, telegram_id, message(config, events, querystart, queryend, mode='md')) # send telegram newsletter
    exit()

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')