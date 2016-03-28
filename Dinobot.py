# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 21:09:34 2015

@author: yorick
"""



# Import some necessary libraries.
import socket 
import io
from time import *
import wikipedia
from urllib import request
import _thread
import sys
import random
import re


queue=[]
greetings=["hello", "hey", "hi", "greetings", "hoi"]
wikitriggers=["what is", "what's", "whats", "who's", "who is", "how do i"]
timers={}
triggers={}
timervals={}
shushed=False
online=True
broken=False
confus=[]
lefts=[]
rights=[]
eyes=[]
mouths=[]
emoticons={}
spacelist=[]         
# Some basic variables used to configure the bot        
server = "irc.web.gamesurge.net" # Server
#channel = "#limittheory" # Channel
channel = "#talstest" # Channel
botnick = "Saoirse2" # Your bots nick

def initialise():
    global spacelist
    global timers
    global triggers
    global timervals
    global confus
    global eyes
    global lefts
    global rights
    global mouths
    global emoticons
    global spacelist
    
    with open('space.txt') as f:
        for line in f:
            spacelist.append(line.strip().replace('"',''))
    
    
    with open('confucius.txt') as f:
       for line in f:
           line=line[line.find('.')+1:].strip()
           confus.append(line)
           
    test="#LEFTS"
    with open('procemo.txt') as f:
        for line in f:
            line=line.strip('\n').strip(' ')
            if line=='':
                pass
            elif line.startswith('#'):
                test=line
            else:
                if test=="#LEFTS":
                    lefts.append(line)
                elif test=="#RIGHTS":
                    rights.append(line)
                elif test=="#EYES":
                    eyes.append(line)
                elif test=="#MOUTHS":
                    mouths.append(line)
    
    with open('emoticons.txt') as f:
        for line in f:
            #print(line)
            line=line.strip('\n').strip(' ').split('&')
            if line[0]=='':
                pass
            else:
                emoticons[line[0]]=line[1]
    print("EMOTICONS")
    print(emoticons)
    with open('triggers.txt') as f:
        for line in f:
            line=line.strip('\n').strip(' ').split('|')
            line[0]=line[0].split('&')
            if line[0][0]=='':
                pass
            else:
                triggers[tuple(line[0])]=line[1].replace("\\n",'\n')
                timers[line[0][0]]=0
                timervals[line[0][0]]=int(line[2])
                
def decrtimer(dur):
    global timers
    for key in timers:
        timers[key]-=dur
        if timers[key]<0:
            timers[key]=0
            
def sleeping(dur):
    sleep(dur)
    decrtimer(dur)

def procemo(chan):
    i=random.randint(1,6)
    test=random.choice(lefts)
    eye=random.choice(eyes)
    test+=eye
    test+=random.choice(mouths)
    if i==6:
        test+=random.choice(eyes)
    else:
        test+=eye
    test+=random.choice(rights)
    print(i)
    sendmsg(chan, test)
    
def ping(mess): # This is our first function! It will respond to server Pings.
    ircsock.send(bytes('PONG %s\r\n' % mess, 'UTF-8'))

def sendmsg(chan , msg, delay=True): # This is the send message function, it simply sends messages to the channel.
    if delay: 
        time=len(msg)/50.0
        sleeping(1)
        msg=msg.split('\n')
    for line in msg:
        ircsock.send(bytes("PRIVMSG "+ chan +" :"+ line +"\n", 'UTF-8') )

def pm(name , msg): # This is the send message function, it simply sends messages to the channel.
    ircsock.send(bytes("PRIVMSG " + name + " :" + msg + "\n", 'UTF-8'))

def joinchan(chan): # This function is used to join channels.
    ircsock.send(bytes("JOIN "+ chan +"\n", 'UTF-8'))

def quitirc(): # This function is used to quit IRC entirely
    global online
    ircsock.send(bytes("QUIT "+" :PUDDING\n", 'UTF-8'))
    online=False
    
def leavechan(chan):
    ircsock.send(bytes("PART "+ chan+" :PUDDING\n", 'UTF-8'))
         
def space(_channel):
    global timers
    if timers['space']<=0:
        sleeping(0.6)
        sendmsg(_channel, random.choice(spacelist))
        timers['space']=200
        
       
def greet(_channel,mess):
    usr=mess[1:mess.find('!')]
    sendmsg(_channel, "Hey "+usr+"!")
    sendmsg(_channel, "o/")
    
def rektwiki(_channel,mess):
    mess=mess[mess.find("rekt wiki"):]
    mess=mess.replace("rekt wiki",'').strip()
    r = request.urlopen("http://lt-rekt.wikidot.com/search:site/q/"+mess.strip().replace(' ','\%20'))
    htmlstr = r.read().decode().replace(' ','').replace('\t','').replace('\n','')
    htmlstr=htmlstr[htmlstr.find("<divclass=\"title\"><ahref=\""):].replace("<divclass=\"title\"><ahref=\"",'')
    htmlstr=htmlstr[:htmlstr.find("\""):].replace("\"",'')
    print(htmlstr+'\n')
    sendmsg(_channel, htmlstr)
    
def confucius(_channel):
    sendmsg(_channel, "Confucius says: "+random.choice(confus))  

def listemo(_channel, mess):
    sendmsg(_channel, "I'll pm you.")
    user=mess[mess.find(":")+1:mess.find("!")]
    for key, value in emoticons.items():
        pm(user, key+": "+value)
   
def wiki(_channel,string, count):
    string=string.strip("'").strip('\r\n').strip("?").strip(".").strip("!").lower()
    string=string.strip()
    if string.startswith("a "):
        string=string[2:]
    elif string.startswith("an "):
        string=string[3:]
    elif string.startswith("the "):
        string=string[4:]
    print(string)
    try: 
        message=wikipedia.summary(string, sentences=count).replace('. ',".\n")
        pageresult=wikipedia.page(string).url.replace('Https://en.wikipedia.org/wiki/','').replace('https://en.wikipedia.org/wiki/','')
    except Exception:
        res = wikipedia.search(string)
        print(res)
        temppage=0
        pageresult=0 
        ref=0
        counter=0
        maxres=5
        test=wikipedia.suggest(string)
        print(test)
        if test== None or test.lower().replace(' ','')!=string.replace(' ',''):
            for stuff in res:
                print(stuff.lower().replace(' ','') )
                print(string.replace(' ',''))
                if stuff.lower().replace(' ','') == string.replace(' ','') : #exact match
                    pageresult=stuff
                    break
                else:
                    try: 
                        temppage=wikipedia.page(stuff)
                        if len(temppage.references)>ref:
                            ref=len(temppage.references)
                            pageresult=stuff
                        counter+=1
                        if counter>maxres:
                            break
                    except wikipedia.exceptions.DisambiguationError as e:
                        #print(e.options)
                        for opt in e.options:
                            try: 
                                temppage=wikipedia.page(opt)
                                if len(temppage.references)>ref:
                                    ref=len(temppage.references)
                                    pageresult=opt
                                counter+=1
                                if counter>maxres:
                                    break
                            except : 
                                pass
                    except KeyError:
                        pass
                    counter+=1
                    if counter>maxres:
                        break
        else:
            pageresult=test
            print(pageresult)
        try: message=wikipedia.summary(pageresult, sentences=count).replace('. ',".\n")
        except wikipedia.exceptions.DisambiguationError as e:
            sendmsg(_channel, "I'm not sure what you mean, i could find:", delay=False)
            i=0
            if count!=1:
                for stuff in e.options:
        
                        sendmsg(_channel, "https://en.wikipedia.org/wiki/"+stuff.replace(' ','_'))
                        message="That's all!"
                        i+=1
                        if i==count:
                            message="There's more but I'm stopping there!!"
                            break
            else:
                message="https://en.wikipedia.org/wiki/"+pageresult.replace(' ','_')
        except Exception as e: 
            print(e)
            message="Something went wrong. It's the fault of the python library makers!"
            sendmsg(_channel, message, delay=False)
            return
    buf=io.StringIO(str(message))
    read=buf.readline()
    testbool=False
    while read!="":  
        sendmsg(_channel, read.strip(), delay=testbool)
        read=buf.readline()
        testbool=True
    if count!=1: sendmsg(_channel, "https://en.wikipedia.org/wiki/"+pageresult.replace(' ','_'))
        

def inpsay():
    cmd = sys.stdin.readline()
    if cmd!="":
        if cmd.startswith("/me"):
            string="ACTION"+cmd[3:].strip('\n')+""
            #print(string)
            sendmsg(channel,string)
        else:
            sendmsg(channel, cmd)
        
def stripleft(string, stuff):
    return string[string.find(stuff)+len(stuff):]
        
initialise()  
                  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutorial covered on http://shellium.org/wiki.\n", 'UTF-8')) # user authentication
ircsock.send(bytes("NICK "+ botnick +"\n", 'UTF-8')) # here we actually assign the nick to the bot

 # Join the channel using the functions we previously defined

while 1: # Be careful with these! it might send you to an infinite loop
    ircmsg = ircsock.recv(2048) # receive data from the server
    buf=io.StringIO(str(ircmsg))
    while True:
        read=buf.readline()
        if read!="":
            queue.append(read)
        else: break
    mess = queue[0] # removing any unnecessary linebreaks.
    mess = mess.strip('\n\r').strip()
    #print(mess) # Here we print what's coming from the server


    if mess.find("Found your hostname") != -1 or mess.find("No ident response") !=-1:
      
      sent="NICK "+ botnick +"\n"+"USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
      ircsock.send(bytes(sent, 'UTF-8')) # here we actually assign the nick to the bot
      print(sent)
      ircsock.send(bytes("PRIVMSG nickserv :iNOOPE\r\n", 'UTF-8'))

    if mess.find("Welcome to the GameSurge IRC") != -1: # if the server pings us then we've got to respond!
        break
    
    if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
        ping(mess)
    
    if len(queue)!=0:
        del queue[0]
      
joinchan(channel)
del queue
queue=[]
print("yay")
def main():
    while online: # Be careful with these! it might send you to an infinite loop
        global shushed
        global broken
        global timers
        timer=time()
        ircmsg = ircsock.recv(2048) # receive data from the server
        try: buf=io.StringIO(str(ircmsg, encoding='utf-8').strip('\r'))
        except Exception: buf=io.StringIO("")
        while True:
            read=buf.readline()
            if read!="":
                queue.append(read)
            else: break
        while len(queue)!=0:
            mess = queue[0] # removing any unnecessary linebreaks.
            print(mess)
            test = mess.strip('\r\n').strip().strip("'")
            mess=test
            lmess=mess.lower()
            _channel=lmess[lmess.find("#"):]
            _channel=_channel[:_channel.find(":")].strip()
            regex1 = re.compile('do+omed')
            regex2 = re.compile('spa+ce')
            #print(_channel)
            if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
                ping(mess)
            if "GameSurge" not in mess and lmess.find(":saoirse!")!=0: 
                if not shushed and "taiya" not in lmess and "jimmy" not in lmess and "quackbot" not in lmess:    
                    if "saoirse" in lmess:
                        if any([greeting in lmess for greeting in greetings]):
                            sendmsg(_channel, random.choice(greetings).title()+"!")
                            
                        lmess=stripleft(lmess,"saoirse")
                        mess=stripleft(mess,"Saoirse")
                        print(lmess)
                        
                        if "join" in lmess:
                            tojoin=lmess[lmess.find("join"):].replace("join",'').strip()
                            joinchan(tojoin)
                            sendmsg(_channel, "To "+tojoin+" and beyond! /o/")
                        elif "leave" in lmess:
                            sendmsg(_channel, "Bye! o/")
                            leavechan(_channel)
                        elif "quit" in lmess:
                            sendmsg(_channel, "Bye! o/")
                            quitirc()
                        elif "shush" in lmess:
                            sendmsg(_channel,"OK, I'll shut up :(")
                            shushed=True
                        elif "initialise" in lmess or "initialize" in lmess:
                            sendmsg(_channel,"OK, reinitialising...")
                            initialise()
                            sendmsg(_channel,"Done! Should work now.")
                        #wikipedia search
                        elif not broken:
                            for stuff in wikitriggers:
                                if stuff in lmess:
                                    lmess=lmess[lmess.find(stuff):]
                                    wiki(_channel,stripleft(lmess,stuff),3)
                                    broken=True
                                    break
                        if broken:
                            break
                        elif "confuc" in lmess or "confusius" in lmess:
                            confucius(_channel)
                        else: sendmsg(_channel,"Pudding!")
                    #no-named things
                    elif "rekt wiki" in lmess:
                        rektwiki(_channel,lmess)
                    elif "TABLEFLIP" in mess:
                        temp="︵ヽ(`Д´)ﾉ︵"
                        for i in range(1,lmess.count('!')):
                            temp+="  "
                            temp="  "+temp
                        temp+="┻━┻ "
                        temp="┻━┻ "+temp
                        sendmsg(_channel,temp) 
                    elif "tableflip" in lmess:
                        temp="(╯°□°）╯︵"
                        for i in range(1,lmess.count('!')):
                            temp+="  "
                        temp+="┻━┻ "
                        sendmsg(_channel,temp) 
                    elif not broken:
                        for key, value in triggers.items():
                            if any([stuff in lmess for stuff in key]):
                                if timers[key[0]]<=0:
                                    sleeping(0.6)
                                    sendmsg(_channel, value)
                                    timers[key[0]]=timervals[key[0]]
                                    broken=True
                    if broken:
                        break
                    elif re.search(regex1, lmess)!=None:
                        sendmsg(_channel,"DOOOOMED!")
                    elif re.search(regex2, lmess)!=None:
                        space(_channel)
                    elif "!procemo" in lmess:
                        procemo(_channel)
                    elif "!listemo" in lmess or "!emoticonlist" in lmess:
                        listemo(_channel, mess)
                    elif not broken:
                        for key, value in emoticons.items():
                            if key in lmess:
                                sendmsg(_channel,value)
                                broken=True
                                break
                    elif broken:
                        break         
                elif "speak" in lmess and "saoirse" in lmess:
                    sendmsg(_channel,"Yay! Pudding!")
                    shushed=False    
            broken=False
            del queue[0]
        timer-=time()
        timer=-timer
        decrtimer(timer)

_thread.start_new_thread(main,())
while True:
    inpsay()
