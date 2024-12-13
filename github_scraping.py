import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
from tqdm import tqdm

def github_topics_scraper(detailed=False, records=True):
    # cek tipe data
    if type(detailed) != bool:
        raise Exception("Expected boolean input for argument 'detailed' but got {}".format(type(detailed)))
    
    if records < 0:
        raise Exception("Number of records can't be negative")
    if type(records) != int:
        if type(records) == bool:
            pass
        else:
            raise Exception("Expected integer or boolean input for the argument 'records' but got {}".format(type(records)))
            
    print('Scraping GitHub topics {}...'.format('in detail' if detailed else ''))

    Topics_details = get_topic_details(records) #ambil data dari halaman GitHub Topics
    
    if records > len(Topics_details['Topic_URL']):
        print('There are only {} topics present on GitHub Topics webpage.'.format(len(Topics_details['Topic_URL'])))
    
    # klo detailed scraping is required =
    if detailed:
        pop_repo_details = get_popular_repo_details(Topics_details['Topic_URL']) #ambil data repositori populer dari setiap topik
        Topics_details.update(pop_repo_details)
    
    print('Scraping completed')

    return pd.DataFrame(Topics_details)

def get_topic_details(records):
    page_content = ''  #  store page content
    start_page = 1     # 'start_page' - GitHub topics pages start from 1 & go till 6
    
    # 'end' calculates how many pages to load based on the required number of records
    end = math.ceil(records / 30) if type(records) == int else (1 if records == True else 6)
    while start_page <= end:
        url = 'https://github.com/topics?page={}'.format(start_page)
        r = requests.get(url)
        if r.status_code != 200:  # kalo error load page
            start_page -= 1       # reload page
        else:
            page_content += '\n' + r.text
        start_page += 1

    soup_doc = BeautifulSoup(page_content, 'html.parser')
    
    # topics
    topics = []
    topic_ptags = soup_doc.find_all('p', {'class': 'f3 lh-condensed mb-0 mt-1 Link--primary'}, limit=records)
    for tag in topic_ptags:
        topics.append(tag.text)
      
    # topics description
    topic_descs = []
    descr_ptags = soup_doc.find_all('p', {'class': 'f5 color-fg-muted mb-0 mt-1'}, limit=records)
    for tag in descr_ptags:
        topic_descs.append(tag.text.strip())
        
    # topic urls
    topic_urls = []
    topic_url_tags = soup_doc.find_all('a', {'class': 'no-underline flex-1 d-flex flex-column'}, limit=records)
    for tag in topic_url_tags:
        topic_urls.append('https://github.com' + tag['href'])
        
    # dict
    topics_dict = {
        'Topics': topics,
        'Description': topic_descs,
        'Topic_URL': topic_urls
    }
    
    return topics_dict

def get_popular_repo_details(topic_urls):
    #  progress bar using tqdm
    pbar = tqdm(total=len(topic_urls))
    
    # dictionary to store the data of popular repositories and their details
    pop_repo_details = {
        'Popular_Repository': [], 'PR_Username': [], 'PR_URL': [], 'Stars': [], 'Forks': []
    }
    
    i = 0
    while i < len(topic_urls):  # topic_urls -> scraped already, utilizing to scrape remaining data
        url = topic_urls[i] + '?o=desc&s=stars'  # creating URL based on the topic
        r = requests.get(url)
        if r.status_code != 200:
            i -= 1                   
        else:     
            pr_soup1 = BeautifulSoup(r.text, 'html.parser')  # creating BeautifulSoup object

            # popular repo name, username, and URL located
            h3_tags = pr_soup1.find_all('h3', {'class': 'f3 color-fg-muted text-normal lh-condensed'}, limit=1)
            
            if h3_tags:  # Check if h3_tags exists
                atags = h3_tags[0].find_all('a')

                # extracting popular repo name, username, and URL
                pop_repo_name = atags[1].text.strip() if len(atags) > 1 else None               # repo name
                pr_username = atags[0].text.strip() if len(atags) > 0 else None                # repo username
                pr_url = 'https://github.com' + atags[1]['href'] if len(atags) > 1 else None    # repo URL 
                
                # scraping number of stars, forked count using pr_url
                if pr_url:
                    r_repo = requests.get(pr_url)
                    if r_repo.status_code == 200:
                        pr_soup2 = BeautifulSoup(r_repo.text, 'html.parser')

                        # locating & extracting tags for star counts
                        star_span_tag = pr_soup2.find('span', {'id': 'repo-stars-counter-star'})
                        stars = int(star_span_tag['aria-label'].split()[0].replace(',', '')) if star_span_tag else None

                        # locating & extracting tags for fork counts
                        forks_span_tag = pr_soup2.find('span', {'id': 'repo-network-counter'})
                        forks = int(forks_span_tag['title'].replace(',', '')) if forks_span_tag else None
                    else:
                        stars, forks = None, None
                else:
                    stars, forks = None, None
                
                # appending scraped data for popular repository to the dictionary
                pop_repo_details['Popular_Repository'].append(pop_repo_name)
                pop_repo_details['PR_Username'].append(pr_username)
                pop_repo_details['PR_URL'].append(pr_url)
                pop_repo_details['Stars'].append(stars)
                pop_repo_details['Forks'].append(forks)

            pbar.update(1)

        i += 1  #next page
    pbar.close()
            
    return pop_repo_details

df = github_topics_scraper(detailed=True, records=False)
df.to_csv('GitHub_topics_detailed.csv')
