import shlex
from argparse import ArgumentParser
import sys
import requests
from datetime import datetime, timedelta

# Root parser -> subparser -> parser -> add arguments
github_parser = ArgumentParser(prog='github')
cmd_parser = github_parser.add_subparsers(dest='command')

trending_repos_parser = cmd_parser.add_parser('trending-repos')
trending_repos_parser.add_argument('--duration',
                                   choices=['day', 'week', 'month', 'year'],
                                   default='week',
                                   help='The duration for trending repos are (day, week, month or year)'
                                   )
trending_repos_parser.add_argument('--limit', help="number of wanted repos", type=int)

while True:
    try:
        user_input = input("Enter your command:")
        cmd_args = shlex.split(user_input)
        args = github_parser.parse_args(cmd_args)
    except SystemExit:
        # Argparse normally kills the script on error;
        # catching SystemExit keeps your loop alive!
        print("Tip: Use 'trending-repos --help' to see valid options.")
        continue

    if args.command == 'exit':
        sys.exit(0)

    elif args.command == 'trending-repos':
        days = 7
        limit = 10

        if args.duration:
            if args.duration == 'day':
                days = 1
            elif args.duration == 'week':
                days = 7
            elif args.duration == 'month':
                days = 30
            elif args.duration == 'year':
                days = 365
        if args.limit:
            limit = args.limit

        date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"created:>{date_limit}",
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }

        try:
            response = requests.get(url, params=params)
            # requests doesn't throw an error just because it got 4XX or 5XX, it will return
            # a response with these status codes so the code will reach "data = response.json()"
            # and the code will crash when decoding that response to JSON
            # so this method will check the status code, if it's 2XX it will continue
            # if it 4XX or 5XX it will throw an exception
            response.raise_for_status()

            data = response.json()
            repos_data = []
            for repo in data['items']:
                repos_data.append({
                    'Repo name': repo['full_name'],
                    'Description': repo['description'],
                    'Stars': repo['stargazers_count'],
                    'Language': repo['language']

                })

            for _ in repos_data:
                print(_)

        except requests.exceptions.HTTPError as err:
            print(f"GitHub API Error: {err}")
        except requests.exceptions.ConnectionError as err:
            print("Network Error: Check your internet connection.")

