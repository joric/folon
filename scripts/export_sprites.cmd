@echo off

rem 1) use [FO4Tools]() to extract "LondonWorldSpace - Interface.ba2\Interface\Pipboy_MapPage.swf"
rem 2) use [JPEX](https://github.com/jindrapetrik/jpexs-decompiler/releases/) to save shapes from Pipboy_MapPage.swf

set fo4=E:\Games\Fallout 4 GOTY
set outdir=.\export

set path=D:\Shared\Tools\Hacking\Games\Bethesda\F4SE\fallout4_tools;%path%
set path=D:\Shared\Tools\Hacking\Games\Bethesda\JPEXS;%path%

set ba2=%fo4%\data\LondonWorldSpace - Interface.ba2

ba2extract.exe "%ba2%" "%outdir%" && del ba2extract.log

set swf=%outdir%\Interface\Pipboy_MapPage.swf

ffdec-cli -onerror ignore -format sprite:svg -export shape "%outdir%\shapes" "%swf%"
ffdec-cli -onerror ignore -format sprite:svg -export sprite "%outdir%\sprites" "%swf%"

rem ffdec-cli -swf2xml "%outdir%\Interface\Pipboy_MapPage.swf" "%outdir%\out.xml"

