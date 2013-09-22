__author__ = 'aub3'
from indexer import *
import re

class ExampleMetadata(Indexer):
    def __init__(self,server):
        super(ExampleMetadata,self).__init__(serverless=False,server=server,project_name='example_metadata_amazon',project_type='Metadata')
        self.regex = re.compile("amazon\.com|stackoverflow\.com|pinterest\.com|walmart\.com")

    def index_file(self,metadata_file):
        self.Data = {}
        try:
            for url,json_string in metadata_file.parse():
                matches = self.regex.findall(json_string.lower())
                if matches:
                    entry = commoncrawl.Metadata.extract_json(url,json_string)
                    if entry:
                        for link in entry['links']:
                            for match in matches:
                                if match in link[0] or match in entry['url']:
                                    self.Data.setdefault(match,[]).append((entry['url'],link[0]))
            metadata_file.clear()
            self.entry_count += len(self.Data)
            if self.Data:
                key= str(self.pid)+'/'+metadata_file.path.split('segment')[1].replace('/','_')
                self.backup_s3(key,self.Data)
        except:
            logging.exception(metadata_file.path)


if __name__ == '__main__':
    if LOCAL:
        example_indexer = ExampleMetadata(server="http://localhost:14080")
    else:
        example_indexer = ExampleMetadata(server="http://www.datamininghobby.com")
    example_indexer.work_loop()


