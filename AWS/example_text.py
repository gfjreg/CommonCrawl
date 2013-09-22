__author__ = 'aub3'
from indexer import *

class TextExample(Indexer):
    def __init__(self,server):
        super(TextExample,self).__init__(serverless=False,server=server,project_name='example_text',project_type='Text')

    def index_file(self,text_file):
        self.Data = []
        try:
            for url,text_content in text_file.parse():
                if 'shop' in text_content.lower() or 'buy' in text_content.lower():
                    self.Data.append((url,text_content))
            text_file.clear()
            self.entry_count += len(self.Data)
            if self.Data:
                key= str(self.pid)+'/'+text_file.path.split('segment')[1].replace('/','_')
                self.backup_s3(key,self.Data)
        except:
            logging.exception(text_file.path)


if __name__ == '__main__':
    if LOCAL:
        text_indexer = TextExample(server="http://localhost:14080")
    else:
        text_indexer = TextExample(server="http://www.datamininghobby.com")
    text_indexer.work_loop()


