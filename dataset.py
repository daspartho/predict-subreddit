import requests
from bs4 import BeautifulSoup
import praw
import re
import csv
import os
import argparse
from dotenv import load_dotenv


# Get CLI args

parser = argparse.ArgumentParser()
parser.add_argument('npage', type=int, help='no of pages to scrape for top subreddits from redditlist.com (1 page => 125 subs)')
parser.add_argument('filename', type=str, help='csv filename to save the dataset to')
args = parser.parse_args()


# Scrapping top subreddits from redditlist.com

npage=args.npage # 125 subs per page
subreddits = []
for n in range(1, npage+1):
    r = requests.get(f"http://www.redditlist.com/?page={n}")
    soup = BeautifulSoup(r.text, 'lxml')
    subreddits.extend([x.text for x in soup.find(id="listing-parent").findAll(class_="span4 listing")[1].findAll("a", attrs={"class": "sfw"})])
subreddits.remove("announcements") # r/announcements is for company statements
subreddits.remove("wallstreetbets") # can't scrape r/wallstreetbets


# Getting top posts titles from subreddits

load_dotenv()

client_id=os.getenv('ID')
client_secret=os.getenv('SECRET')
user_agent=os.getenv('AGENT')

reddit = praw.Reddit(
    client_id=os.getenv('ID'),
    client_secret=os.getenv('SECRET'),
    user_agent=os.getenv('AGENT'),
    check_for_async=False,
)

rows=[]
for subreddit_name in subreddits:
    print(f'scraping {subreddit_name}')
    subreddit = reddit.subreddit(subreddit_name) 

    for post in subreddit.top(limit=None):
        title = post.title
        title = re.sub("\[.*?\]",'',title) # removing flair information from title
        title = '"'+title+'"' # wrapping inside double quotes to deal with commas in the title text
        rows.append([title, subreddit_name])


# Writing the tiles to csv file
with open(args.filename, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["title", "label"]) # headers
    writer.writerows(rows)

print("All Done!")