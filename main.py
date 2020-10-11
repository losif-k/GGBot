import asyncio
import glob
import json
import os
import random
from datetime import datetime

import discord

import covid
import log
import mp3
import ytdl

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


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
list_msg = None
playnext = True
keepplaying = True
vch_list = []
vol = 0.15
recentuser = None
goingtodiscon = False


def is_me(m):
    return m.author == client.user


def is_privileged(u):
    return u in guild.get_role(694430139395735642).members


@client.event
async def on_message(message):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    global vc, playnext, play_msg, keepplaying, vol, list_msg, recentuser, goingtodiscon
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
                                          '<파일번호1> [파일번호2] 옵션{r - 랜덤}...\n`볼륨\n**',
                              color=0x00ff00)
        sent = await channel.send(embed=embed)
        await asyncio.sleep(60)
        await sent.delete()

    if content.startswith("`목록"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(
            f"목록 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        flist = mp3.getflist()
        first_index = 0
        max_page = int(flist.__len__() / 25 + 1)
        if flist.__len__() > 25:
            if content[4:].isdigit():
                if int(content[4:]) - 1 * 25 <= flist.__len__():
                    first_index = (int(content[4:]) - 1) * 25
                    flist = flist[first_index:]
                    if flist.__len__() > 24:
                        flist = flist[0:24]
                else:
                    first_index = 0
                    if first_index + 24 < flist.__len__():
                        flist = flist[0:24]
            else:
                first_index = 0
                if first_index + 24 < flist.__len__():
                    flist = flist[0:24]

        embed = discord.Embed(title=":floppy_disk: **List** :floppy_disk:",
                              description=f'{int((first_index + 1) / 25 + 1)}/{max_page}', color=0xff8f00)
        for i in range(len(flist)):
            if flist[i]:
                if flist[i].endswith('.mp3'):
                    if flist[i].startswith('yt|'):
                        title = flist[i].split('|')[1]
                        embed.add_field(name=i + 1 + first_index, value=title)
                    else:
                        title = flist[i].replace("_", "-").replace('.mp3', '')
                        embed.add_field(name=i + 1 + first_index, value=title)
        if list_msg is not None:
            await list_msg.delete()
            list_msg = None
        list_msg = await channel.send(embed=embed)

    if content.startswith("`del"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(
            f"del Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        num = content[5:]
        if num.isdecimal():
            mp3.delSource(int(num))

    if content.startswith("`재생"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(
            f"재생 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
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
        if 'a' in fid:
            fid = []
            for i in range(1, flist.__len__() + 1):
                fid.append(str(i))
        for i in fid:
            if i.isdigit():
                if int(i) < 1 or int(i) > flist.__len__() + 1:
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
            if not vc.is_connected():
                vc = await vch.connect()
            if vc.is_playing():
                sent = await channel.send('응 재생중이야~')
                await asyncio.sleep(5)
                await sent.delete()
                return
            play_msg = None
            nextfile = None
            if plist.__len__() > i + 1:
                nextfile = flist[plist[i + 1]]
            audiosrc = mp3.getSource(plist[i] - 1, vol=vol)
            keepplaying = True
            vc.play(audiosrc[1])
            log.writelog(f"Playing as filename : {audiosrc[3]}")
            des = f'\t\t최근 사용자 : {recentuser.mention}\n{audiosrc[3].split("|")[1] if audiosrc[3].startswith("yt|") else audiosrc[3].replace(".mp3", "")}'
            if nextfile:
                des = des + \
                    f'\n다음 : {nextfile.split("|")[1] if nextfile.startswith("yt|") else nextfile.replace(".mp3", "")}'
            if audiosrc[3].startswith('yt|'):
                embed = discord.Embed(
                    title=f":arrow_forward:", description=des, color=0x00ff2c + i)
                embed.add_field(
                    name="Youtube", value=f'https://www.youtube.com/watch?v={audiosrc[3].split("|")[2]}', inline=False)
            else:
                embed = discord.Embed(
                    title=f":arrow_forward:", description=des, color=0x00ff2c + i)
            play_msg = await channel.send(embed=embed)
            await play_msg.add_reaction(":bee3:684780556860653753")
            await play_msg.add_reaction(":stop:709351389855481867")
            while vc.is_playing():
                await asyncio.sleep(1)
                if not keepplaying:
                    vc.stop()
            if play_msg:
                await play_msg.delete()
            play_msg = None
            if not playnext:
                break
        sent = await channel.send(f'정지 {recentuser.mention}')
        await asyncio.sleep(5)
        await sent.delete()

    if content.startswith("`yt"):
        if not is_privileged(author):
            return
        if message.channel in tch_list:
            await message.delete()
        log.writelog(
            f"yt Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        param = content[4:]
        if len(param) == 11:
            x = threading.Thread(target=ytdl.ytdownload, args=(param,))
            x.start()

    if content.startswith("`볼륨"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(
            f"볼륨 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
        arg = content[4:].replace(' ', '')
        if arg.__len__() > 0 and arg.isdigit():
            if 0 < int(arg) <= 100:
                vol = int(arg) / 100
        embed = discord.Embed(
            title="**볼륨**", description=f'{int(vol * 100)}%', color=0xff2f00)
        sent = await channel.send(embed=embed)
        await asyncio.sleep(5)
        await sent.delete()

    if content.startswith("`ch"):
        if message.channel in tch_list:
            await message.delete()
        if not is_privileged(author):
            return
        log.writelog(
            f"ch Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
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
        log.writelog(
            f"코로나 Executed {channel}({channel.id}) | {audpname}({auid}) -{content}")
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
    global guild, guild_id, tch, tch_id, vch, vch_id, vch_list, vc
    guild = client.get_guild(guild_id)
    for ch in client.get_all_channels():
        if ch.type is discord.ChannelType.voice:
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

client.run(os.getenv('DISCORD_TOKEN'))
