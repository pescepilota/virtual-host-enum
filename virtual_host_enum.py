import threading, queue, random, string, requests, argparse

host_file_wordlist = None
user_thread = 5
target_ip = None
resume = None

class VirtualHostBruter():
    def __init__(self, host_wordlist):
        self.host_wordlist = host_wordlist
        self.error_page = None
        self.found = False
        self.headers = None

    def run_bruteforce(self):
         headers = {'User-agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                 'Host': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) }
         self.error_page = requests.get('http://'+target_ip, headers=headers)
         
         for i in range(user_thread):
             t = threading.Thread(target=self.vhost_bruter)
             t.start()

    def vhost_bruter(self):
        while not self.host_wordlist.empty() and not self.found:
            vhost = self.host_wordlist.get().rstrip()
            print("Trying: {} ({} left)".format(vhost, self.host_wordlist.qsize()))

            headers = {'User-agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0','Host': vhost} 
            try:
                r = requests.get('http://'+target_ip, headers=headers)
            except:
                print("Request error for {}, maybe you can find something...".format(vhost))
                r = None
                
            if r.text != self.error_page.text:
                 print("Host found! : {}".format(vhost))

                    
def build_wordlist(wordlist_file):
    # read in the word list
    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()
    found_resume = False
    words = queue.Queue()
    for word in raw_words:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from: %s" % resume)
        else:
            words.put(word)
    return words


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Enter the target ip")
    parser.add_argument("wordlist", help="Enter the wordlist path")
    
    args = parser.parse_args()
    target_ip = args.target
    host_file_wordlist = args.wordlist
    
    host_list = build_wordlist(host_file_wordlist)
    bruter_obj = VirtualHostBruter(host_list)
    bruter_obj.run_bruteforce()


