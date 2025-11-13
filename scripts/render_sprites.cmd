@echo off

mkdir ..\images\sprites 2>nul

setlocal enabledelayedexpansion
for %%F in (.\export\shapes\*.svg) do (
    rem magick -density 192 -background none "%%F" -gravity center -extent 64x64 "sprites\%%~nF.png"
    magick -density 192 -background none "%%F" -gravity center -extent 64x64 -alpha set -fill "rgba(255,255,255,0.1)" -opaque none -fill "rgba(0,0,0,0)" -draw "color 0,0 floodfill" "..\images\sprites\%%~nF.png"
)


