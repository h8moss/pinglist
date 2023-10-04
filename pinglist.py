import argparse
from bs4 import BeautifulSoup
import requests


def create_parser():
  parser = argparse.ArgumentParser(
    prog="PingList", 
    description="Ping a list of URLS and show output"
  )

  parser.add_argument('urls', nargs='*', help='Urls to ping')

  parser.add_argument('-i', '--input',
                      dest='inputFile',
                      help='file containing a url per line to ping',
                      type=argparse.FileType('w')
  )

  parser.add_argument("-o", "--output-file", 
                      dest="outputFile",
                      type=argparse.FileType('w'),
                      help="The file in which to output the results"
  )

  parser.add_argument('-f', '--format',
                      choices=['csv', 'list', 'md', 'none'],
                      default="list",
                      dest="format",
                      help="Format for the program's output",
  )
  parser.add_argument('--output-format',
                      choices=['csv', 'list', 'md'],
                      default='csv',
                      dest='outputFormat',
                      help='Format for the output file, ignored if --output-file is not passed'
  )

  parser.add_argument('--delay', '-d',
                      default=0,
                      dest='delay',
                      help='Delay between requests, in milliseconds',
                      type=int
  )

  parser.add_argument('--silent', 
                      action='store_true',
                      dest='silent',
                      help='If passed, the program will not display progress and instead only display the result once done',
  )

  parser.add_argument('--timeout',
                      default=5000,
                      dest='timeout',
                      help='Time to pass for request to be discarded',
                      type=int,
  )

  return parser

def get_title(request_body, default_value):
  parser = BeautifulSoup(request_body, 'html.parser')
  if parser.title == None:
    return default_value
  return parser.title

def show_progress(current, total):
  divisions = 50
  progress = round((divisions * current)/total)
  print('[', end='')
  for i in range(divisions):
    if i < progress:
      print('@', end='')
    else:
      print('-', end='')
  print(f'] - {current}/{total}', end='\r')

  if (current == total):
    print('')

def display_data(data):
  print('END')

def main():
  parser = create_parser()
  args = parser.parse_args()

  urls = []

  for url in args.urls:
    url = str(url)
    if not url.startswith('http://') and not url.startswith('https://'):
      url = 'http://' + url
    urls.append(url)

  if args.inputFile != None:
    with open(args.inputFile, 'r') as f:
      lines = f.readlines()
      for line in lines:
        line = str(line)
        while '\n' in line or '\r' in line:
          line.replace('\n', '')
          line.replace('\r', '')

        if not line.startswith('http://') and not line.startswith('https://'):
          line = 'http://' + line
        urls.append(line)

  data = []
  for i in range(len(urls)):
    url = urls[i]
    # url, title, status code, status message, server
    try:
      r = requests.get(url)
      title = get_title(r.content, url)
      status = r.status_code
      status_message = r.reason
      server = r.headers.get('Server', "UNKNOWN")
      content_length = len(r.content if r.content else [])
    except requests.exceptions.RequestException:
      title = url
      status = 0
      status_message = "could not connect"
      server = "UNKNOWN"
      content_length = 0

    data.append({
      url: url,
      title: title,
      status: status,
      status_message: status_message,
      server: server,
      content_length: content_length
    })
    if not args.silent:
      show_progress(i+1, len(urls))

  display_data(data)
  
if __name__ == '__main__':
  main()

# * -h
# * -i, --input 
# * -o, --output-file
# * -f, --format (csv, list, md, NONE)
# * --output-format
# * --delay, -d
# * --silent (don't show progress bar)
# * --timeout