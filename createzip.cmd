del plugin.video.unofficialkissanime.zip
rmdir /s /q plugin.video.unofficialkissanime
mkdir plugin.video.unofficialkissanime
copy *py plugin.video.unofficialkissanime
copy *xml plugin.video.unofficialkissanime
copy icon.png plugin.video.unofficialkissanime
copy README.md plugin.video.unofficialkissanime
xcopy /E resources plugin.video.unofficialkissanime\resources\
"C:\Program Files\7-Zip\7z.exe" a plugin.video.unofficialkissanime-0.0.1.zip plugin.video.unofficialkissanime\
