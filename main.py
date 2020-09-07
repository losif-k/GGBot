import asyncio  # asyncio.sleep를 위한 import
import glob
import json  # config.json 파일 처리를 위한 import
import os
import random
import threading
from datetime import datetime

import discord  # discordpy : https://discordpy.readthedocs.io/en/latest/api.html
from mcstatus import MinecraftServer

import covid  # 코로나 바이러스 웹 파싱
import log  # log기록 함수
import mp3  # mp3파일 관련 함수
import ytdl

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# 추가 파일

with open('config.json') as f:
    config = json.load(f)
    guild_id = config['guild_id']
    tch_id = config['tch_id']
    vch_id = config['vch_id']
    dmchlist = config['dmchlist']

client = discord.Client()
guild: discord.Guild
tch = None
vch = None
vc = None
play_msg = None
pause_msg = None
list_msg = None
playnext = True
keepplaying = True
tch_list = []
vch_list = []
vol = 0.15
recentuser = None
goingtodiscon = False
lock = False

def is_me(m):
    return m.author == client.user


def is_privileged(u):
    return u in guild.get_role(694430139395735642).members




@client.event
async def on_message(message):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    global tch, tch_id, vch, vch_id, guild, vc, playnext, play_msg, pause_msg, keepplaying, vol, list_msg, recentuser, goingtodiscon, lock
    channel = message.channel
    content = str(message.content)
    audpname = message.author.display_name
    auid = message.author.id
    author = message.author

    if is_me(message):
        return

    print(
        f"[{date_time}]{channel}({channel.id}) |  {audpname}({auid}): {content}")

    '''
    if content.startswith(명령어):
        if message.channel in tch_list:
            await message.delete()
        log.writelog(f"{명령어} Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        ...
    '''
    if content.startswith('`명령어'):
        if message.channel in tch_list:
            await message.delete()
        embed = discord.Embed(title="**명령어**",
                              description='**`코로나\n`목록\n`yt 11자리 코드\n`재생'
                                          '<파일번호1> [파일번호2] 옵션{r - 랜덤}...\n`볼륨\n'
                                          '`채널 [채널번호]\n`del**',
                              color=0x00ff00)
        sent = await channel.send(embed=embed)
        await asyncio.sleep(60)
        await sent.delete()

    if content.startswith("`목록"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(f"목록 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        msg = ''
        flist = mp3.getflist()
        for i in range(len(flist)):
            if flist[i]:
                if flist[i].endswith('.mp3'):
                    if flist[i].startswith('yt|'):
                        tmp = flist[i].split('|')[1]
                        msg = msg + f'**{i}** | {tmp.replace("_", "-")}\n'
                    else:
                        msg = msg + f'**{i}** | {flist[i].replace("_", "-")}\n'
        msg = msg.replace('.mp3', '')
        embed = discord.Embed(title=":floppy_disk: **MP3** :floppy_disk: ", description=msg, color=0xff8f00)
        if list_msg is not None:
            await list_msg.delete()
            list_msg = None
        list_msg = await channel.send(embed=embed)
        await list_msg.add_reaction("🔁")

    if content.startswith("`del"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(f"del Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        num = content[5:]
        if num.isdecimal():
            mp3.delSource(int(num))

    if content.startswith("`재생") :
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(f"재생 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        recentuser = author
        keepplaying = True
        fid = content[4:]
        if len(fid) < 1:
            sent = await channel.send(":interrobang: ")
            await asyncio.sleep(5)
            await sent.delete()
            return
        fid = fid.split(' ')
        flist = mp3.getflist()
        plist = []
        randomplay = False
        if 'r' in fid:
            randomplay = True
            fid.remove('r')
        else:
            for i in fid:
                if i.isdigit():
                    if int(i) < 0 or int(i) > flist.__len__():
                        continue
                    else:
                        plist.append(int(i))
                else:
                    continue
        if randomplay:
            tmplist = []
            for i in range(plist.__len__()):
                tmp = random.choice(plist)
                tmplist.append(tmp)
                plist.remove(tmp)
            plist = tmplist
        playnext = True
        goingtodiscon = False
        for i in range(plist.__len__()):
            if vc == None:
                vc = await vch.connect()
            if vc.is_playing():
                vc.stop()
                playnext = False
                await asyncio.sleep(1.5)
            if play_msg:
                await play_msg.delete()
            if pause_msg:
                await pause_msg.delete()
            play_msg = None
            pause_msg = None
            nextfile = None
            discord.Embed.video
            if plist.__len__() > i + 1:
                nextfile = flist[plist[i + 1]]
            audiosrc = mp3.getSource(plist[i], vol=vol)
            if audiosrc[0]:
                keepplaying = True
                vc.play(audiosrc[1])
                log.writelog(f"Playing as filename : {audiosrc[3]}")
                des = f'\t\t최근 사용자 : {recentuser.mention}\n{audiosrc[3].split("|")[1] if audiosrc[3].startswith("yt|") else audiosrc[3].replace(".mp3", "")}'
                if nextfile:
                    des = des + f'\n다음 : {nextfile.split("|")[1] if nextfile.startswith("yt|") else nextfile.replace(".mp3", "")}'
                if audiosrc[3].startswith('yt|'): 
                    embed = discord.Embed(title=f":arrow_forward:", description=des, color=0x00ff2c + i)
                    embed.add_field(name="Youtube", value=f'https://www.youtube.com/watch?v={audiosrc[3].split("|")[2]}', inline=False)
                else:
                    embed = discord.Embed(title=f":arrow_forward:", description=des, color=0x00ff2c + i)
                play_msg = await channel.send(embed=embed)
                await play_msg.add_reaction(":bee3:684780556860653753")
                await play_msg.add_reaction(":stop:709351389855481867")
                while vc.is_playing():
                    await asyncio.sleep(1)
                    if not keepplaying:
                        vc.stop()
                keepplaying = False
                if play_msg:
                    await play_msg.delete()
                play_msg = None
            else:
                log.writelog(f"as Error user input : {f}")
                sent = await channel.send(audiosrc[2])
                await asyncio.sleep(5)
                await sent.delete()
                goingtodiscon = True
                lock = False
                for i in range(120):
                    await asyncio.sleep(1)
                    if not goingtodiscon:
                        break
                    if i == 119:
                        await vc.disconnect()
                        vc = None
                return
            if not playnext:
                break
        if keepplaying:
            goingtodiscon = False
        sent = await channel.send(f'정지 {recentuser.mention}')
        await asyncio.sleep(5)
        await sent.delete()
        for i in range(120):
            await asyncio.sleep(1)
            if not goingtodiscon:
                break
            if i == 119:
                await vc.disconnect()
                vc = None

    if content.startswith("`yt"):
        if not is_privileged(author):
            return
        log.writelog(f"yt Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        param = content[4:]
        if len(param) == 11:
            x = threading.Thread(target=ytdl.ytdownload, args=(param,))
            x.start()

    if content.startswith("`볼륨"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(f"볼륨 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        arg = content[4:].replace(' ', '')
        if arg.__len__() > 0 and arg.isdigit():
            if 0 < int(arg) <= 100:
                vol = int(arg) / 100
        embed = discord.Embed(title="**볼륨**", description=f'{int(vol * 100)}%', color=0xff2f00)
        sent = await channel.send(embed=embed)
        await asyncio.sleep(5)
        await sent.delete()

    if content.startswith("`ch"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(f"ch Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        arg = content[4:].replace(' ', '')
        if arg.__len__() > 0 and arg.isdigit():
            if guild.get_channel(int(arg)) is not None:
                vch_id = int(arg)
                vch = guild.get_channel(vch_id)
            elif int(arg) < vch_list.__len__():
                vch_id = vch_list[int(arg)].id
                vch = vch_list[int(arg)]
            else:
                sent = await channel.send(":interrobang: ")
                await asyncio.sleep(5)
                await sent.delete()
                return
            if vc is not None:
                await vc.move_to(vch)
        d = ''
        for i in range(len(vch_list)):
            if vch is vch_list[i]:
                d = d + f"**{i} | {vch_list[i].name}({vch_list[i].id})**\n"
                continue
            d = d + f"{i} | {vch_list[i].name}({vch_list[i].id})\n"
        embed = discord.Embed(title="**채널목록**", description=d, color=0xff2f00)
        sent = await channel.send(embed=embed)
        await asyncio.sleep(5)
        await sent.delete()


    if content.startswith("`코로나"):
        if message.channel in tch_list:
            await message.delete()
        log.writelog(f"코로나 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        data = covid.getdatancov()
        embed = discord.Embed(title=f"**({data[0]})코로나19 정보**",
                              description=f"**확진환자 : {data[1]} 명**\n **격리해제 : {data[2]} 명**\n**검사진행 : {data[3]}명**\n**사망자 : {data[4]}명**",
                              color=0xff2f00)
        await channel.send(embed=embed)
    if author.id == 400115094929014797:
        None
    return


@client.event
async def on_ready():
    global guild, guild_id, tch, tch_id, vch, vch_id, tch_list, vch_list, vc
    guild = client.get_guild(guild_id)
    for ch in client.get_all_channels():
        if ch.type is discord.ChannelType.text:
            tch_list.append(ch)
        elif ch.type is discord.ChannelType.voice:
            vch_list.append(ch)
        else:
            continue
    tch = guild.get_channel(tch_id)
    vch = guild.get_channel(vch_id)
    print('\n\n\n\nLogged in as')
    print(f"{client.user.name}({client.user.id})")
    print('------------------------------------------------------------')
    print('Server Info')
    print(f"{guild.name}({guild.id})")
    print(f"TextChannel List : ")
    for ch in tch_list:
        print(f"{ch.name}({ch.id})")
    print(f"VoiceChannel List : ")
    for ch in vch_list:
        print(f"{ch.name}({ch.id})")
    print('------------------------------------------------------------')
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("`명령어로 명령어 확인"))
    await tch.purge(limit=200, check=is_me)


@client.event
async def on_reaction_add(reaction, user):
    global play_msg, keepplaying, playnext, recentuser, list_msg
    if play_msg is not None:
        users = await reaction.users().flatten()
        if reaction.message.id == play_msg.id:
            if type(reaction.emoji) is str or not reaction.emoji.id in [709351389855481867, 684780556860653753]:
                await reaction.clear()
                return
            if reaction.emoji.id in [709351389855481867, 684780556860653753]:
                if reaction.count > 1:
                    for u in users:
                        if is_privileged(u):
                            if reaction.emoji.id == 709351389855481867:
                                playnext = False
                                keepplaying = False
                                recentuser = user
                            elif reaction.emoji.id == 684780556860653753:
                                keepplaying = False
                                recentuser = user
    if list_msg is not None:
        if reaction.message.id == list_msg.id:
            if reaction.emoji == '🔁':
                if reaction.count > 1:
                    log.writelog(f"Playlist Refreshed")
                    msg = ''
                    flist = mp3.getflist()
                    for i in range(len(flist)):
                        if flist[i]:
                            if flist[i].endswith('.mp3'):
                                if flist[i].startswith('yt|'):
                                    tmp = flist[i].split('|')[1]
                                    msg = msg + f'**{i}** | {tmp.replace("_", "-")}\n'
                                else:
                                    msg = msg + f'**{i}** | {flist[i].replace("_", "-")}\n'
                    msg = msg.replace('.mp3', '')
                    embed = discord.Embed(title=":floppy_disk: **MP3** :floppy_disk: ", description=msg, color=0xff8f00)
                    channel = list_msg.channel
                    if list_msg is not None:
                        await list_msg.delete()
                        list_msg = None
                    list_msg = await channel.send(embed=embed)
                    await list_msg.add_reaction("🔁")

client.run(os.getenv('DISCORD_TOKEN'))
