DS Photo
----
[Synology](https://www.synology.com) [Photo Station](https://www.synology.com/en-us/dsm/app_packages/PhotoStation) albums browser for [KODI](http://kodi.tv/)

----
##Setup Synology hack

To correctly work with KODI we need to do small hack on Synology. Hack is to setup redirection from `/photo-redirect.jpg` to real path `/photo/webapi/thumb.php`. To do this login to Synology with SSH and in folder `/volume1/web` create file `.htaccess`. Edit file and put those two line into it
 ```
 RewriteEngine On
 Redirect "/photo-redirect.jpg" "/photo/webapi/thumb.php"
 ```

---
##Setup add-on

After installing add-on please open `settings` and set `Host name`, `User Name`, `Password`
