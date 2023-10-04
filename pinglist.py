import argparse

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