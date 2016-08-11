del plugin.video.unofficialkissanime.zip
rmdir /s /q plugin.video.unofficialkissanime
mkdir plugin.video.unofficialkissanime
copy *py plugin.video.unofficialkissanime
copy *xml plugin.video.unofficialkissanime
xcopy /E resources plugin.video.unofficialkissanime\resources\
dir /s plugin.video.unofficialkissanime 
"C:\Program Files\7-Zip\7z.exe" a plugin.video.unofficialkissanime.zip plugin.video.unofficialkissanime\
