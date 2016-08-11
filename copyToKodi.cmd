rmdir /s /q plugin.video.unofficialkissanime
mkdir plugin.video.unofficialkissanime
copy *py plugin.video.unofficialkissanime
copy *xml plugin.video.unofficialkissanime
copy icon.png plugin.video.unofficialkissanime
copy README.md plugin.video.unofficialkissanime
xcopy /E resources plugin.video.unofficialkissanime\resources\
xcopy /E /Y plugin.video.unofficialkissanime "%appdata%\kodi\addons\plugin.video.unofficialkissanime\"
del /S /Q "%appdata%\kodi\addons\plugin.video.unofficialkissanime\*pyo"