#!/usr/bin/env python
#
#    This file is part of ESA.
#
#    ESA is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ESA.  If not, see <http://www.gnu.org/licenses/>.
#
##########################
# PROGRAMMER: Andrew Michalski
# Version: 0.2.2
# LAST UPDATE: APR 1, 2016
##########################
import sys
import imaplib
import email
import smtplib
import os
import hashlib
import time
import mail_cmd #

## CONSTANTS LOADED FROM CONFIG FILE ##
f = open('data/config.txt','r')
for line in f:
        if line.split()[0] == 'IMAPSRV':
                IMAPSRV = line.split()[1]
        elif line.split()[0] == 'EMAILADDR':
                EMAILADDR = line.split()[1]
        elif line.split()[0] == 'SMTPSRV':
                SMTPSRV = line.split()[1]
        elif line.split()[0] == 'REFRESH':
                REFRESH = int(line.split()[1])
        elif line.split()[0] == 'PASSWORD':
                PASSWORD = line.split()[1]

# LOAD COMMANDS FROM FILE
cmd = {'ADMIN':[],'SUPERVISOR':[],'USER':[]}
f = open('data/cmd.txt','r')
for line in f:
        for c in line.split()[1].split(','):
                cmd[line.split()[0]].append(c)
f.close()
purgatory = {}
tasks = []
msgid = 0

## FUNCTIONS ##
def read_mail(M):
	"""Reads Mail"""
	gotMail = False
	recv, data = M.search(None, "ALL")
	if recv != 'OK':
		print("NO MESSAGES") # 4TESTING ONLY
		return False
	for num in data[0].split():
		gotMail = True
		recv, data = M.fetch(num, '(RFC822)')
		if recv != "OK":
			print("ERROR ON MESSAGE "+num+"\nDELETING...")#ERROR MSG
			return gotMail
		msg = email.message_from_string(data[0][1])
		# parse info
		sender = msg['From'].split()[-1][1:-1]
		subject = msg['Subject'].split()
		# do whatever
		if subject[0] == 'CONFIRM':
			global purgatory
			try:
				if purgatory[subject[1]][0] == sender:
					send_mail(sender, str(mail_cmd.EXECUTE(purgatory[subject[1]])))
					os.remove(purgatory[subject[1]][1])
			except:
				pass
		elif subject[0] in cmd['ADMIN'] and sender in mail_cmd.group_lookup('ADMIN'):
			code = create_job(sender,msg,"ADMIN")
			msg = "Subject: Confirm "+subject[0]+"\n\nAn email from this address made the following request:\n"+' '.join(subject)+"\nIf you wish to process this request send an email back to this address with the subject line:\n\nCONFIRM "+code+"\n\nIf you did not send this request notify the Administrator. If this becomes a reoccuring problem, consider using a lockout/lockdown code if available."
			send_mail(sender, msg)
		elif subject[0] in cmd['SUPERVISOR'] and sender in mail_cmd.group_lookup('SUPERVISOR'):
			code = create_job(sender,msg,"SUPERVISOR")
			msg = "Subject: Confirm "+subject[0]+"\n\nAn email from this address made the following request:\n"+' '.join(subject)+"\nIf you wish to process this request send an email back to this address with the subject line:\n\n"+"CONFIRM "+code+"\n\nIf you did not send this request notify the Administrator. If this becomes a reoccuring problem, consider using a lockout/lockdown code if available."
			send_mail(sender, msg)
		elif subject[0] in cmd['USER'] and sender in mail_cmd.group_lookup('USER'):
			code = create_job(sender,msg,"USER")
			msg = "Subject: Confirm "+subject[0]+"\n\nAn email from this address made the following request:\n"+' '.join(subject)+"\nIf you wish to process this request send an email back to this address with the subject line:\n\n"+"CONFIRM "+code+"\n\nIf you did not send this request notify the Administrator. If this becomes a reoccuring problem, consider using a lockout/lockdown code if available."
			send_mail(sender, msg)
		M.store(num, '+FLAGS', '\\Deleted')
	M.expunge()
	return gotMail
	
def send_mail(to, msg):
	srv = smtplib.SMTP(SMTPSRV)
	srv.starttls()
	srv.login(EMAILADDR, PASSWORD)
	srv.sendmail(EMAILADDR, to, str(msg))
	srv.quit()

def create_job(sender, msg, perm):
	"""Saves message and creates confirmation code"""
	global purgatory
	global msgid
	confirm = os.urandom(128)
	confirm = hashlib.md5(confirm).hexdigest()[:32]
	path = 'pending/'+str(msgid)+'_'+confirm+'.txt'
	purgatory[confirm] = []
	purgatory[confirm].append(sender)
	purgatory[confirm].append(path)
	purgatory[confirm].append(perm)
	f = open(path,'w')
	f.write(str(msg))
	f.close()
	msgid += 1
	return confirm

def schedule():
        # CHECK TIME
        from datetime import datetime, timedelta
        now = datetime.now()
        f = open('data/tasks.txt','r+')
        while 1:
                try:
                        st = f.tell()
                        line = f.readline()
                        when, repeat = line.split()[0:2]
                        todo = line.split()[2:]
                        when = datetime.strptime(when,'%Y,%m,%d,%H,%M')
                        if now > when:
                                mail_cmd.EXECUTE(todo)
                                if repeat[0].upper() == 'D':
                                        when += timedelta(days=int(repeat[1:]))
                                elif repeat[0].upper() == 'W':
                                        when += timedelta(weeks=int(repeat[1:]))
                                # SAVE TO TASKS
                                prepend = f.read()
                                f.seek(st)
                                when = when.strftime("%Y,%m,%d,%H,%M")
                                line = when+' '+repeat+' '+' '.join(todo)+'\n'
                                f.write(line+prepend)
                                f.truncate()
                except:
                        break
        f.close()


### MAIN #task##
# CONNECT TO SERVER
i = 0 # COUNTER FOR schedule()
M = imaplib.IMAP4_SSL(IMAPSRV)
try:
	M.login(EMAILADDR, PASSWORD)
except:
	print("LOGIN FAILED")
	sys.exit(1)
# READ FROM INBOX
while 1:
        recv, data = M.select("INBOX")
        if recv == "OK":
                print("CHECKING MAIL...") # TESTING PURPOSES ONLY
                try:
                        repeat = read_mail(M)
                except:
                        print("A problem has occured... retry in 3 seconds.")
                        sleep(3)
                        continue
                M.close()
        else:
                print("FAILED TO SELECT INBOX")
        if repeat == False:
                time.sleep(REFRESH)
        i += 1
        if i >= 1:
                i = 0
                schedule()
M.logout()
