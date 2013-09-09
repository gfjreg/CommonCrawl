__author__ = 'aub3'
import gzip,json,logging,os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from settings import AWS_KEY,AWS_SECRET,STORE_PATH
from hadoop.io import SequenceFile



CONN = S3Connection(AWS_KEY,AWS_SECRET)
class CommonCrawl:
    def __init__(self,refresh=False,raw_file=False):
        self.files = self.get_files(refresh)
        self.metadata = [line.strip() for line in self.files if line.strip() and "metadata" in line]
        self.text = [line.strip() for line in self.files if line.strip() and "text" in line]
        self.raw = [line.strip() for line in self.files if line.strip() and ".arc" in line]
        self.other = [line.strip() for line in self.files if line.strip() and ".arc" not in line and "text" not in line and "metadata" not in line]


    def get_files(self,refresh=False):
        """
            This function downloads valid_segments.txt and then scans S3 for all files present in the valid segments.
        """
        if not refresh:
            try:
                fh = gzip.open("files.gz")
                files = fh.readlines()
                fh.close()
            except:
                print "could not load files.gz attempting a refresh and generating files.gz"
                refresh = True
        if refresh:
            CONN = S3Connection(AWS_KEY,AWS_SECRET)
            bucketname = 'aws-publicdatasets'
            bucket = CONN.get_bucket(bucketname)
            getter = Key(bucket)
            getter.key = 'common-crawl/parse-output/valid_segments.txt'
            getter.get_contents_to_filename('valid_segments')
            prefix='common-crawl/parse-output/segment/'
            segments = [line.strip() for line in file('valid_segments')]
            files = [key.name.encode('utf-8') for segment in segments for key in bucket.list(prefix+str(segment))]
            fh = gzip.open('files.gz','w')
            fh.write('\n'.join(files))
            fh.close()
        return files

    def store_individual(self):
        fh = gzip.open('metadata.gz','w')
        fh.write('\n'.join(self.metadata))
        fh.close()
        fh = gzip.open('text.gz','w')
        fh.write('\n'.join(self.text))
        fh.close()
        fh = gzip.open('raw.gz','w')
        fh.write('\n'.join(self.raw))
        fh.close()

class Crawl_Sequence_File(object):
    def __init__(self,key,local_directory):
        self.key = key
        self.path = local_directory+self.key.replace("/","_")
        self.urls = []

    def local(self):
        if os.path.isfile(self.path):
            return True
        else:
            return False

    def download(self):
        try:
            bucketname = 'aws-publicdatasets'
            bucket = CONN.get_bucket(bucketname)
            getter = Key(bucket)
            getter.key = self.key
            getter.get_contents_to_filename(self.path)
        except:
            logging.exception("could not retrieve metadata file: "+self.key)

    def parse(self):
        if not self.local():
            self.download()
        for url,json_string in self.read_sequence_file():
            self.urls.append(url)
            yield url,json_string


    def read_sequence_file(self):
        "reads the sequence file using hadoop.io python library"
        reader = SequenceFile.Reader(self.path)
        key_class = reader.getKeyClass()
        value_class = reader.getValueClass()
        key = key_class()
        value = value_class()
        while reader.next(key, value):
            yield key.toString(),value.toString()
        reader.close()

    def clear(self):
        if self.local():
            os.remove(self.path)



class Metadata(Crawl_Sequence_File):
    @classmethod
    def extract_json(cls,url,json_string):
        json_entry = json.loads(json_string)
        if 'content' in json_entry:
            entry = {'url':url,'title':'','links':[]}
            if 'title' in json_entry['content']:
                entry['title'] = json_entry['content']['title']
            if 'links' in json_entry['content']:
                for link in json_entry['content']['links']:
                    text = ''
                    href = ''
                    if 'text' in link:
                        text = link['text']
                    if 'href' in link:
                        href = link['href']
                    entry['links'].append((href,text))
            return entry
        return None


class Text(Crawl_Sequence_File):
    pass



if __name__ == '__main__':
    crawl = CommonCrawl()
    print "number of metadata files",len(crawl.metadata),crawl.metadata[:5]
    print "number of text files",len(crawl.text),crawl.text[:5]
    print "number of raw files",len(crawl.raw),crawl.raw[:5]
    crawl.store_individual()
    metadata_files = [Metadata(key,STORE_PATH) for key in crawl.metadata]
    for test in metadata_files[:10]:
        for url,json_string in test.parse():
            print test.key,test.path,url
            break
    text_files = [Text(key,STORE_PATH) for key in crawl.text]
    for test in text_files[:10]:
        for url,text in test.parse():
            print test.key,test.path,url
            break

