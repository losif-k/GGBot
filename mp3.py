import os

import discord


def getSource(arg, vol):
    flist = getflist()
    if arg < len(flist):
        des = f'**{flist[arg]}**'
        return [True,
                discord.PCMVolumeTransformer(original=discord.FFmpegPCMAudio("./mp3_files/" + flist[arg]), volume=vol),
                des,
                flist[arg]]
    else:
        return [False, 0, f"{arg} 번은 없닭"]

def delSource(arg):
    flist = getflist()
    if arg < len(flist):
        os.remove('./mp3_files/' + flist[arg])

def getflist():
    tmp = os.listdir("mp3_files/")
    tmp.sort()
    yt_list = []
    list = []
    for f in tmp:
        if f.startswith("Youtube-"):
            yt_list.append(f)
        else:
            list.append(f)
    flist = list + yt_list
    return flist