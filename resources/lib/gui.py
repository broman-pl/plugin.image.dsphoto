import xbmcplugin, xbmcgui
import sys

class GUI:
    def __init__(self):
        print '[DSPHOTO GUI]'
        self.handler = 0

    def setHandler(self, handler):
        self.handler = handler

    def setContent(self, contentType='files'):
        xbmcplugin.setContent(int(sys.argv[1]), contentType)

    def addItem(self, item):
        print '[DSPHOTO GUI] add item'
        isFolder = False
        numberOfItems = 0

        thumb = None
        if 'thumb' in item:
            thumb = item['thumb']

        liz = xbmcgui.ListItem(item['name'], '', thumbnailImage=thumb)
        if 'itemType' in item:
            liz.setInfo(type='picture', infoLabels={'Title': item['name']})

        if 'folder' in item:
            isFolder = True

        if 'total' in item:
            numberOfItems = item['total']

        url = sys.argv[0]
        if 'params' in item:
            url = sys.argv[0] + item['params']

        if 'url' in item:
            url = item['url']

        print 'url: ' + url

        xbmcplugin.addDirectoryItem(handle=self.handler, url=url, listitem=liz, isFolder=isFolder)


    def endDir(self):
        print '[DSPHOTO GUI] end dir'
        #liz = xbmcgui.ListItem('test', '')
        #xbmcplugin.addDirectoryItem(handle=self.handler, url='https://i.ytimg.com/vi/uSEoNUgUqlY/maxresdefault.jpg', listitem=liz, isFolder=False)


        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
