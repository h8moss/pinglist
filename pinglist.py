import argparse
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import requests
from time import sleep
import warnings


def create_parser():
    parser = argparse.ArgumentParser(
        prog="PingList",
        description="Ping a list of URLS and show output"
    )

    parser.add_argument('urls', nargs='*', help='Urls to ping')

    parser.add_argument('-i', '--input',
                        dest='inputFile',
                        help='file containing a url per line to ping',
                        type=argparse.FileType('r')
                        )

    parser.add_argument("-o", "--output-file",
                        dest="outputFile",
                        type=argparse.FileType('w'),
                        help="The file in which to output the results"
                        )

    parser.add_argument('-f', '--format',
                        choices=['csv', 'list', 'md', 'table', 'none'],
                        default="list",
                        dest="format",
                        help="Format for the program's output",
                        )
    parser.add_argument('--output-format',
                        choices=['csv', 'list', 'table', 'md'],
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
                        help='Time to pass for request to be discarded, in milliseconds',
                        type=int,
                        )

    return parser


def get_title(request_body, default_value):
    parser = BeautifulSoup(request_body, 'html.parser')
    if parser.title == None:
        return default_value
    return parser.title.text


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


def get_formatted_data(data, format):
    if format == 'none':
        return ''

    text = ''

    # header
    if format == 'csv':
        text += 'Url,Title,Status code,Status message,Server,Content length\n'
    elif format == 'list':
        pass  # list does not need header
    elif format == 'md':
        text += '|Url|Title|Status code|Status message|Server|Content length|\n'
        text += '|-|-|-|-|-|-|\n'
    elif format == 'table':
        text += 'Url\t\t\tTitle\tStatus code\tStatus message\tServer\tContent length\n'
    else:
        raise ValueError(f'Unrecognized format: {format}')

    for data_item in data:
        url = data_item['url']
        title = data_item['title']
        status_code = data_item['status']
        status_message = data_item['status_message']
        server = data_item['server']
        content_length = data_item['content_length']
        if format == 'csv':
            text += f'{url},{title},{status_code},{status_message},{server},{content_length}\n'
        elif format == 'list':
            text += f'- {title} ({url}) ({status_code} {status_message}) {server} {content_length}\n'
        elif format == 'table':
            text += f'{url}\t{title}\t{status_code}\t\t{status_message}\t\t{server}\t{content_length}\n'
        else:
            text += f'|{url}|{title}|{status_code}|{status_message}|{server}|{content_length}|\n'

    return text


def main():

    warnings.filterwarnings('ignore', XMLParsedAsHTMLWarning)

    parser = create_parser()
    args = parser.parse_args()

    urls = []

    for url in args.urls:
        url = str(url)
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        urls.append(url)

    if args.inputFile != None:
        lines = args.inputFile.readlines()
        for line in lines:
            line = str(line)
            while '\n' in line or '\r' in line:
                line = line.replace('\n', '')
                line = line.replace('\r', '')

            if not line.startswith('http://') and not line.startswith('https://'):
                line = 'http://' + line
            urls.append(line)

    data = []
    for i in range(len(urls)):
        url = urls[i]
        try:
            if args.delay > 0:
                sleep(args.delay/1000)
            r = requests.get(url, timeout=args.timeout/1000)
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
            'url': url,
            'title': title,
            'status': status,
            'status_message': status_message,
            'server': server,
            'content_length': content_length
        })
        if not args.silent:
            show_progress(i+1, len(urls))

    print(get_formatted_data(data, args.format))
    if args.outputFile != None:
        args.outputFile.write(get_formatted_data(data, args.outputFormat))


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
