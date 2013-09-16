__author__ = 'aub3'
from indexer import *

class ExampleMetadata(Indexer):
    def __init__(self,server):
        super(ExampleMetadata,self).__init__(server=server,project_name='example_metadata',project_type='Metadata')

    def index_file(self,metadata_file):
        self.Data = []
        try:
            for url,json_string in metadata_file.parse():
                if 'amazon.com' in json_string.lower():
                    entry = commoncrawl.Metadata.extract_json(url,json_string)
                    if entry:
                        for link in entry['links']:
                            if "amazon.com" in link[0] or "amazon.com" in link[1]:
                                self.Data.append((entry['url'],link[0],link[1]))
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


