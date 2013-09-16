__author__ = 'aub3'
from indexer import *

class AmazonRCM(Indexer):
    def __init__(self,server):
        super(AmazonRCM,self).__init__(server=server,project_name='rcm_amazon',project_type='Metadata',query_status=False)

    def index_file(self,metadata_file):
        self.Data = []
        try:
            for url,json_string in metadata_file.parse():
                if 'rcm.amazon' in json_string.lower():
                    entry = commoncrawl.Metadata.extract_json(url,json_string)
                    if entry:
                        for link in entry['links']:
                            if "rcm.amazon" in link[0] or "rcm.amazon" in link[1]:
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
        amazon_indexer = AmazonRCM(server="http://localhost:14080")
    else:
        amazon_indexer = AmazonRCM(server="http://www.datamininghobby.com")
    amazon_indexer.work_loop()


