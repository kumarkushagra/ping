from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from typing import Optional

import time
import pymongo

class Notice(BaseModel):
    date: str
    title: str
    notice_url: str
    published_by: Optional[str] = None
    department: Optional[str]=None


class NoticeScraper:
    def jsonify_soup(self,soup):
        all_notices = []
        for row in soup.find_all('tr'):
            a = row.find('a')
            if a:
                try:
                    # Extract data
                    title = a.text.strip()
                    link = a['href']
                    date = row.find('td').text.strip().split()[0]

                    # Safely extract 'Published By' information
                    b_tags = row.find_all('b')
                    publisher_info = b_tags[-1].text.replace("Published By:", "").strip().split(",")
                    
                    published_by = publisher_info[0].strip()
                    # Handle cases where department might be the same as publisher
                    department = publisher_info[-1].strip() if len(publisher_info) > 1 else published_by

                    # Create a dictionary for the current notice
                    # The keys match your Pydantic model for easy integration
                    notice_dict = {
                        "date": date,
                        "title": title,
                        "notice_url": link,
                        "published_by": published_by,
                        "department": department,
                        "processed":False
                    }

                    # Add the dictionary to our list
                    all_notices.append(notice_dict)

                except (IndexError, AttributeError) as e:
                    # This will catch errors if 'b_tags' is empty, 'a' is missing,
                    # or other parsing issues occur.
                    # print(f"Skipping a row due to parsing error: {e}")
                    continue

        # json_output = json.dumps(all_notices, indent=4)
        return all_notices
           
    def upload_db(self, scraped_notices):
        myclient = pymongo.MongoClient("mongodb+srv://admin:asdf%401234@ping.uskhf3w.mongodb.net/")
        mydb = myclient["learnDB"]
        mycol = mydb["Notices"]
        # mycol.create_index("notice_url", unique=True)


        for notice in scraped_notices:
            # x = mycol.insert_many(notice)
            try:
                x = mycol.insert_one(notice)
                print(x.inserted_id)
            except Exception as e:
                print("[W]:" , e)
                break
    
    def run(self):
        while(True):    
            response = requests.get("https://www.imsnsit.org/imsnsit/notifications.php")
            soup = BeautifulSoup(response.content, 'html.parser') 
            scraped_notices = self.jsonify_soup(soup)
            self.upload_db(scraped_notices)
            time.sleep(20*60)
            
            
if __name__=="__main__":
    scraper = NoticeScraper()
    scraper.run()