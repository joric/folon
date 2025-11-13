@echo off

mkdir sprites

setlocal enabledelayedexpansion
for %%F in (.\export\shapes\*.svg) do (
    magick -density 180 -background none "%%F" -gravity center -extent 64x64 "sprites\%%~nF.png"
)


