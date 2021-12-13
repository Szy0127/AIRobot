import urllib.parse as parse
from urllib.request import urlretrieve
import requests
import json
import os
import time
import sys
import vlc
from time import sleep
class Music:
    def __init__(self):
        self.downloadURL = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.song&searchid=63229658163010696&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&%s&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
        self.url = '''https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey5559460738919986&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data={"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"1825194589","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"1825194589","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":0,"format":"json","ct":24,"cv":0}}'''
        self.path = './QQmusic'
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.media = vlc.MediaPlayer()

    def get_download_url(self,song_name:str,song_index :int = 0):
        w = parse.urlencode({'w': song_name})
        url = self.downloadURL % (w)
        content = requests.get(url=url)
        str_1 = content.text
        dict_1 = json.loads(str_1)
        song_list = dict_1['data']['song']['list']
        url_list = []
        music_name = []

        for i in range(len(song_list)):
            music_name.append(song_list[i]['name'] + '-' + song_list[i]['singer'][0]['name'])

            print('{}.{}-{}'.format(i + 1, song_list[i]['name'], song_list[i]['singer'][0]['name']))
            url_list.append(self.url % (song_list[i]['mid']))

        content_json = requests.get(url=url_list[song_index])
        dict_2 = json.loads(content_json.text)
        url_ip = dict_2['req']['data']['freeflowsip'][1]
        purl = dict_2['req_0']['data']['midurlinfo'][0]['purl']
        return  music_name[song_index] , url_ip + purl

    def exist(self,name):
        musics = os.listdir(self.path)
        exists = False
        for music in musics:
            if name in music:
                return True
        return False


    def download(self,name):
        try:
            '''
            if self.exist(name):
                filename = self.path + '/'+ name + '.mp3'
                return filename
            '''
            music_name , url = self.get_download_url(name)
            filename = self.path + '/' + music_name + '.mp3'
            if self.exist(name):
                return url
            print('开始下载',name)
            urlretrieve(url = url, filename= filename)
            print('{}.mp3下载完成！'.format(music_name))
            return filename
        except Exception as e:
            print(e)
    
    def resume(self):
        self.media.set_pause(0)

    def pause(self):
        self.media.pause()

    def getMusic(self,name):
        res = self.download(name)
        if res:
            self.media.set_mrl(res)
            return True
        else:
            return False
    def play(self):
        self.media.play()
        while self.media.is_playing():
            time.sleep(1)
    def release(self):
        self.media.release()
if __name__ == '__main__':
    music = Music()
    music.play('下雨天')

'''
import vlc
p = vlc.MediaPlayer(url)
p.play()                                            #直接播放

import time
time.sleep(5)

while p.is_playing():                        #每隔0.5秒循环一次，直到音乐播放结束
    time.sleep(0.5)
'''
