import requests, os, sys
from lxml import html

RPGURL_FILEINFO = "https://rapidgator.net/api/v2/file/info/"
RPGURL_FOLDERINFO = "https://rapidgator.net/api/v2/folder/info"
RPGURL_FILEDOWNLOAD = "https://rapidgator.net/api/v2/file/download/"
RPG_XPATH_FILENAME = "//div[@class='text-block file-descr']//p//a//text()"

class URLType(str, Enum):
    FOLDER = "folder"
    FILE = "file"


class Client:

    BASE_URL = "https://rapidgator.net/api/v2/"

    USERNAME = None
    PASSWORD = None
    PATH = None
    LISTOFDOWNLOAD = None

    TOKEN = None

    def __init__(self, username=None, password=None):
        
        # if not len(sys.argv) == 5:
        #     print ("Argument should be python rapidgatordl.py {USERNAME-premiumuser} {PASSWORD} {FULL PATH OF FILE dl.txt} {SAVE TO DIRECTORY}")
        #     sys.exit(0)

        self.USERNAME = username
        self.PASSWORD = password

        self.PATH = sys.argv[4]
        self.LISTOFDOWNLOAD = sys.argv[3]

        self.generate_token()

        #Validate
        # if not os.path.exists(PATH) and os.path.isdir(PATH) :
        #     print("Save Directory not exist")
        #     sys.exit(0)
        # if not os.path.exists(LISTOFDOWNLOAD) and os.path.isfile(LISTOFDOWNLOAD) :
        #     print("List of download url not exist")
        #     sys.exit(0)
        
    def generate_token(self):
        PARAMS = {"login": self.USERNAME, "password": self.PASSWORD}
        response = requests.get(url=f"{self.BASE_URL}user/login", params=PARAMS)
        data = response.json()
        print(f"data : {str(data)}")
        self.TOKEN = data["response"]["token"]        

    def _request(self, method: str, path: str, data: dict = None, params: dict = None):
        _params = {
            "token": self.TOKEN
        }
        if params:
            _params = {
                **_params
                **params
            }
        response = requests.request(
            method=method, 
            url=f"{self.BASE_URL}{path}", 
            data=data, 
            params=_params
        )
        return response

    def file_info(self, file_id: str):
        return self._request(
            method="GET",
            path="file/info/",
            params={
                "file_id": file_id
            }
        )

    def folder_info(self, folder_id: str):
        return self._request(
            method="GET",
            path="folder/info/",
            params={
                "folder_id": folder_id
            }
        )

    def download_file(self, file_id: str):
        return self._request(
            method="GET",
            path="file/download/",
            params={
                "file_id": file_id
            }
        )


def retrieve_folder(_url):
    pass


def parse_file_download(response):
    data = response.json()
    print(data)
    _dl_url = data["response"]["download_url"]
    print(f"Response :{str(data)} \n getDownloadLink: {_dl_url}")
    return _dl_url


def parse_file_info(response):
    ## If want assign filename from URL (htttp://rg.to/file/408320/assign_filename_by_yourself.rar ==> file_name = assign_filename_by_yourself.rar
    # try:
    #     file_name = _url.split("/")[5]
    #     file_name = file_name.replace(".html", "")
    #     print("expect file name : " + file_name)
    # except:
    #     print("file name not found")
    #     file_name = str(int(round(time.time() * 1000)))
    ## end If

    ## If want get filename from original uploader
    if response.status_code > 400 :
        print(f"URL : {_url} get HTTP STATUS {str(response.status_code)}")
        file_name = _file_id
    else :
        root = html.fromstring(response.text)
        tree = root.getroottree()
        result = root.xpath(RPG_XPATH_FILENAME)
        file_name = ''.join([word.strip() for word in result])
        file_name = len(file_name) > 0 and file_name or _file_id
    ## end IF
    return file_name
    # download_file(filename, _url)


def get_url_type(url):
    """ 
    Determines if the given url is a file or a folder.
    Folder urls look like: `http://rapidgator.net/folder/414/test.html`
    File urls look like: `http://rapidgator.net/file/267796c7b59efd11126606dbde8dd1e4/test-setup.exe`

    """ 
    if "folder" in url:
        return URLType.FOLDER
    return URLType.FILE


def main():
    """
    Main function
    """
    api = Client(
        username=sys.argv[1],
        password=sys.argv[2]
    )

    with open(LISTOFDOWNLOAD) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            print(f"File {cnt}: {line.strip()}")
            file_name = None
            _url = line.strip()

            if not _url :
                print("++END++")
                sys.exit(0)

            url_type = get_url_type(_url)
            if url_type(_url) == URLType.FILE:
                _file_id = _url.split("/")[4]
                response = api.file_info(_file_id)
                file_name = parse_file_info(response)
                response = api.download_file(_file_id)
                parse_file_download(response)
                download_cmd = f"wget -P {api.PATH} -O '{api.PATH}/{file_name}{_dl_url}"
                print(download_cmd)
                os.system(download_cmd)
            elif url_type == URLType.FOLDER:
                pass
            else:
                print(f"Could not determine url type. for url: {_url}")
            line = fp.readline()
            cnt += 1



if __name__ == "__main__":
    main()