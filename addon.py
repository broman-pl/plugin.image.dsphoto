#!/usr/bin/python
# coding=utf-8
import xbmcaddon, xbmcgui, xbmcplugin, xbmc
import urllib, urllib2
import json
import sys, os

dsphoto = xbmcaddon.Addon()
BASE_RESOURCE_PATH = os.path.join(dsphoto.getAddonInfo('path'), 'resources')
sys.path.append(os.path.join(BASE_RESOURCE_PATH, 'lib'))

import gui

addon = xbmcaddon.Addon('plugin.image.ds-photo')
addonName = addon.getAddonInfo('name')

path_auth = '/photo/webapi/auth.php'
path_info = '/photo/webapi/info.php'
path_album = '/photo/webapi/album.php'
path_smart_albums = '/photo/webapi/smart_album.php'
path_thumb = '/photo/webapi/thumb.php'
redirect_thumb_path = '/photo-redirect.jpg'
path_photos='/photo/webapi/photo.php'

IMAGES_PATH = os.path.join(xbmc.translatePath(addon.getAddonInfo('path')), 'resources', 'images')

search_icon = os.path.join(IMAGES_PATH, 'configure-icon.png')
albums_icon = os.path.join(IMAGES_PATH, 'configure-icon.png')
settings_icon = os.path.join(IMAGES_PATH, 'configure-icon.png')

class DsPhoto(xbmcgui.Window):
    def __init__(self):
        self.host = self.getSetting('host')
        self.username = self.getSetting('username')
        self.password = self.getSetting('password')
        self.items_limit = self.getSetting('page_limit')

        print "[DSPHOTO] initialization"
        self.arguments = sys.argv[2][1:]
        self.gui = gui.GUI()
        self.params = {}
        self.handler = int(sys.argv[1])
        self.gui.setHandler(self.handler)
        self.sid = ''
        self.offset = 0
        self.page = 0
        self.errorMessage = ''

    def onAction(self, action):
        print "[DSPHOTO] onAction called " + str(action)

    def onClick(self, controlId):
        print "[DSPHOTO] onClick called" + controlId

    def getAuth(self):
        print "[DSPHOTO] get SID"
        url = 'http://' + self.host + path_auth
        print "[DEBUG] DSPHOTO: authorisation url " + url
        values = dict(
            username=self.username,
            password=self.password,
            api='SYNO.PhotoStation.Auth',
            method='login',
            version='1'
        )

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        try:
            rsp = urllib2.urlopen(req)
            content = rsp.read()
            data = json.loads(content)

            self.sid = data['data']['sid']
            return True
        except Exception, e:
            self.errorMessage = e
            return False

    def mainMenu(self):
        print '[DSPHOTO] show main menu ' + self.sid
        self.gui.setContent()
        sid = self.sid
        if not sid:
            sid = ''

        if self.host and self.username and self.password:
            total = 4
            self.gui.addItem({'name': 'albums', 'params': '?action=albums&sid=' + sid, 'folder': True, 'thumb': albums_icon, 'total': total})
            self.gui.addItem({'name': 'smart albums', 'params': '?action=smart&sid=' + sid, 'folder': True, 'thumb': albums_icon, 'total': total})
            self.gui.addItem({'name': 'search', 'params': '?action=search&sid=' + sid, 'folder': True, 'thumb': search_icon, 'total': total})
        else:
            total = 1

        self.gui.addItem({'name': 'settings', 'params': '?action=settings&sid=' + sid, 'folder': True, 'thumb': settings_icon, 'total': total})

        self.gui.endDir()

    def albumsList(self, parentAlbumId=None):
        print '[DSPHOTO] list album content'

        self.gui.setContent()
        url = 'http://' + self.host + path_album
        values = dict(
            sid=self.sid,
            sort_by='filename',
            sort_direction='asc',
            offset=self.offset,
            limit=self.items_limit,
            recursive='false',
            api='SYNO.PhotoStation.Album',
            method='list',
            type='album,video,photo',
            additional='album_permission,thumb_size,photo_exif,video_quality,video_codec,album_sorting,rating',
            version='1'
        )

        if parentAlbumId is not None:
            values['id'] = parentAlbumId

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)

        rsp = urllib2.urlopen(req)
        content = rsp.read()
        print content
        data = json.loads(content)

        if data['success']:
            total = data['data']['total']
            offset = data['data']['offset']

            for item in data['data']['items']:
                thumb = 'http://' + self.host + path_thumb + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=small&id=' + item['id'] + '&sid=' + self.sid

                if item['type'] == 'album':
                    self.gui.addItem({'name': item['info']['title'], 'params': '?action=albums&albumid=' + item['id'] + '&sid=' + self.sid, 'folder': True, 'total': total, 'thumb': thumb})

                if item['type'] == 'photo' and item['info']['rating'] >= 0:
                    photo_url = 'http://' + self.host + redirect_thumb_path + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=large&id=' + item['id'] + '&sid=' + self.sid + '&file=photo.jpg'
                    self.gui.addItem({'name': item['info']['title'], 'url': photo_url, 'total': total, 'thumb': thumb, 'itemType': 'pictures'})

            if int(total) > int(offset):
                self.gui.addItem({'name': 'Next page', 'params': '?action=albums&albumid=' + parentAlbumId + '&sid=' + self.sid + '&page=' + str(self.page + 1), 'folder': True, 'total': total, 'thumb': thumb})


        self.gui.endDir()

    def smartAlbum(self):

        self.gui.setContent()
        url = 'http://' + self.host + path_smart_albums
        values = dict(
            sid=self.sid,
            sort_by='title',
            sort_direction='asc',
            offset=self.offset,
            limit=self.items_limit,
            api='SYNO.PhotoStation.SmartAlbum',
            method='list',
            additional='thumb_size',
            version='1'
        )

        data = urllib.urlencode(values)
        print '[DSPHOTO] ' + data
        headers = {'Cookie' : 'PHPSESSID=' + self.sid}
        req = urllib2.Request(url, data, headers)

        rsp = urllib2.urlopen(req)
        content = rsp.read()
        print content

        data = json.loads(content)

        if data['success']:
            total = data['data']['total']

            for item in data['data']['smart_albums']:
                thumb = 'http://' + self.host + path_thumb + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=small&id=' + item['id'] + '&sid=' + self.sid
                self.gui.addItem({'name': item['name'], 'params': '?action=smart&albumid=' + item['id'] + '&sid=' + self.sid, 'folder': True, 'total': total, 'thumb': thumb})

        self.gui.endDir()

    def smartAlbumPhotos(self, albumId):
        self.gui.setContent()
        url = 'http://' + self.host + path_photos
        values = dict(
            sid=self.sid,
            additional='photo_exif,video_codec,video_quality,thumb_size',
            api='SYNO.PhotoStation.Photo',
            filter_smart=albumId,
            limit=self.items_limit,
            method='list',
            offset=0,
            sort_by='filename',
            sort_direction='asc',
            type='photo,video',
            version=1
        )
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)

        rsp = urllib2.urlopen(req)
        content = rsp.read()
        print content
        data = json.loads(content)
        if data['success']:
            total = data['data']['total']

            for item in data['data']['items']:
                thumb = 'http://' + self.host + path_thumb + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=small&id=' + item['id'] + '&sid=' + self.sid
                photo_url = 'http://' + self.host + redirect_thumb_path + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=large&id=' + item['id'] + '&sid=' + self.sid + '&file=photo.jpg'
                self.gui.addItem({'name': item['info']['title'], 'url': photo_url, 'total': total, 'thumb': thumb, 'itemType': 'pictures'})

        self.gui.endDir()


    def showPhoto(self, photoId=None):
        print '[DSPHOTO show photo + ' + str(photoId)

        url = 'http://' + self.host + path_thumb + '?api=SYNO.PhotoStation.Thumb&method=get&version=1&size=large&id=' + photoId + '&sid=' + self.sid + '&file=photo.jpg'
        xbmc.executebuiltin('ShowPicture('+url+')')

    def handleRequest(self):
        print '[DSPHOTO] handle request'
        print '[DSPHOTO] arguments :' + sys.argv[2]
        self.parseParams()

        albumId = None
        if 'page' in self.params:
            self.page = int(self.params['page'])
            self.offset = (self.items_limit * self.page) + 1

        if 'sid' in self.params:
            print '[DSPHOTO we have sid in params'
            self.sid = self.params['sid']

        if len(self.sid) == 0:
            if self.host and not self.getAuth():
                title = 'ERROR'
                message = 'error: ' + str(self.errorMessage)
                self.errorMessage = ''

                xbmc.executebuiltin("XBMC.Notification(" + title + ", " + message + ")")

        if 'action' in self.params:

            if self.params['action'] == 'albums':
                if 'albumid' in self.params:
                    albumId = self.params['albumid']
                self.albumsList(albumId)

            if self.params['action'] == 'smart':
                if 'albumid' in self.params:
                    albumId = self.params['albumid']
                    self.smartAlbumPhotos(albumId)
                else:
                    self.smartAlbum()

            if self.params['action'] == 'photo':
                if 'photoid' in self.params:
                    photoId = self.params['photoid']

                self.showPhoto(photoId)

            if self.params['action'] == 'settings':
                xbmcaddon.Addon().openSettings()
        else:
            self.mainMenu()

    def parseParams(self):
        if "=" in self.arguments:
            try:
                self.params = dict()
                for x in self.arguments.split("&"):
                    elems = x.split("=")
                    if len(elems) == 2:
                        self.params[elems[0]] = elems[1]
            except:
                print '[DSPHOTO] error in params: ' + self.arguments

        print self.params

    def getSetting(self, name):
        return xbmcplugin.getSetting(int(sys.argv[1]), name);

dsPhoto = DsPhoto()
dsPhoto.handleRequest()

del dsPhoto

print '[DSPHOTO] end of script'
