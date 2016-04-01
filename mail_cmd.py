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
def DELTASK():
        """DELTASK [task]"""
        global sender
        global subject
        task = subject[1].split('/')[-1]
        f = open('data/tasks.txt','r+')
        while 1:
                try:
                        st = f.tell()
                        line = f.readline()
                        dt, repeat, creator, fname = line.split()
                        if fname == '/data/tasks/'+task:
                                if sender == creator or sender in group_lookup('ADMIN'):
                                        append = f.read()
                                        f.seek(st)
                                        f.write(append)
                                        f.truncate()
                                        import os
                                        os.remove('/data/tasks/'+task)
                        f.close()
                except:
                        break

def TASKVIEW():
        """TASKVIEW [*task]"""
        global sender
        global subject
        if sender in group_lookup('ADMIN'):
                permit = True
        f = open('data/tasks.txt','r')
        if permit == True:
                ret = 'Subject: TASKVIEW SUCCESSFUL\n\n'+f.read()
        else:
                ret = 'Subject: TASKVIEW SUCCESSFUL\n\n**ONLY SHOWING TASKS SET BY YOU**'
                for line in f:
                        if line.split()[2] == sender:
                                ret += line + '\n'
        f.close()
        try:
                task = subject[1].split('/')[-1]
                f = open('data/tasks/'+task,'r')
                ret += '\n\nTASK: '+ task + '\n\n'
                ret += f.readline()+'\n'
                f.close()
        except:
                pass
        return ret

def REMIND():
        """REMIND [group] AT [mmddyyyyHHMM] THAT [command-word-word] REPEAT [increment]"""
        global subject
        global sender
        global msg
        global information
        import email
        try:
                group = subject[1]
                if subject[2].upper() == 'AT':
                        dt = subject[3]
                        c = 4
                else:
                        dt = subject[2]
                        c = 3
                if subject[c].upper() == 'THAT':
                        c += 1
                newsub = ' '.join(subject[c].split('-'))
                c += 1
                if subject[c].upper() == 'REPEAT':
                        c += 1
                repeat = subject[c]
                # SANITY CHECK
                try:
                        if len(group_lookup(group)) < 1:
                                int('s') # Raises exception if invalid input
                        int(dt)
                        if not len(dt) == 12:
                                int('s') # Raises exception if invalid input
                        int(repeat[1:])
                        if not repeat[0].upper() in ['D','W','M']:
                                int('s') # Raises exception if invalid input
                except:
                        return 'Subject: REMIND FAILED\n\nInput is impropper.'
        except:
                return 'Subject: REMIND FAILED\n\nCheck syntax.'
        # Write message to file.
        boring = True
        content = 'Subject: '+newsub+'\n'
        for line in msg.as_string().split('\n'):
                if boring == False:
                        content += line+'\n'
                elif line[:8].upper() == 'SUBJECT:':
                        boring = False
        # GET FNAME (POSSIBLE MD5 COLLISION)
        import os, hashlib
        fname = os.urandom(128)
        fname = hashlib.md5(fname).hexdigest()[:32]
        f = open('data/tasks/'+fname+'.txt','w')
        f.write(content)
        f.close()
        # SET TASK
        f = open('data/tasks.txt','a')
        line = dt[4:8]+','+dt[0:2]+','+dt[2:4]+','+dt[8:10]+','+dt[10:]+' '+repeat+' '+sender+' data/tasks/'+fname+'.txt '+information[2]
        f.write(line+'\n')
        f.close()
        return 'Subject: REMIND SUCCESSFUL\n\n'
        
def BROADCAST():
        """BROADCAST [group]/[files] TO [group]. Send message to group"""
        global subject
        global sender
        try:
                path = subject[1].split('/')[0].upper()
                fname = subject[1].split('/')[1].upper()
        except:
                return 'Subject: BROADCAST FAILED\n\nCheck syntax.'
        if len(subject) > 2:
                group = subject[-1].upper()
        else:
                return 'Subject: BROADCAST FAILED\n\nNot enough arguments'
        # DETERMINE PERMISSIONS
        if sender in group_lookup(path) and group_lookup(group)[0] == sender:
                # LOAD FILE
                try:
                        f = open('files/'+path+'/'+fname+'.txt','r')
                        content = f.read()
                        content = "Subject: NOTIFICATION\n"+content[content.find('\n\n')+2:]
                        f.close()
                except:
                        return 'Subject: BROADCAST FAILED\n\nFile does not exist.'
                # SEND FILE TO GROUP(S)
                f = open('data/config.txt','r')
                for line in f:
                        if line.split()[0] == 'SMTPSRV':
                                SMTPSRV = line.split()[1]
                        elif line.split()[0] == 'EMAILADDR':
                                EMAILADDR = line.split()[1]
                        elif line.split()[0] == 'PASSWORD':
                                PASSWORD = line.split()[1]
                f.close()
                # SEND
                import smtplib
                server = smtplib.SMTP(SMTPSRV)
                server.starttls()
                server.login(EMAILADDR, PASSWORD)
                server.sendmail(sender, group_lookup(group), content)
                server.quit()
                return 'Subject: BROADCAST SUCCESSFUL\n\n'+group
        else:
                return 'Subject: BROADCAST FAILED\n\nYou do not have permission.'

def DELGROUP():
        """DELGROUP [group]. Deletes a group if user is admin. DOES NOT DELETE GROUP FILES"""
        global subject
        global sender
        try:
                group = subject[1]
        except:
                return 'Subject: DELGROUP FAILED\n\nCheck Syntax'
        if group in ['ADMIN','SUPERVISOR','USER']:
                return 'Subject: DELGROUP FAILED\n\nThis group cannot be deleted.'
        if sender in group_lookup('ADMIN'):
                f = open('data/group/'+group[0].upper()+'.txt','r+')
                # DELETE LINE FOR GROUP
                rem = False
                pre = ''
                post = ''
                for line in f:
                        if line.split()[0] == group.upper():
                                rem = True
                                continue
                        if not rem:
                                pre += line
                        else:
                                post += line
                f.seek(0)
                f.write(pre+post)
                f.truncate()
                f.close()
                return 'Subject: DELGROUP SUCCESSFUL\n\n'+group.upper()+' has been deleted.\nConsider KICKing group supervisor from SUPERVISOR if they no longer need supervisor permissions.'
        else:
                return 'DELGROUP FAILED\n\nYou do not have permission'

def LOOKUP():
        """LOOKUP [group]. Shows users in a group."""
        global sender
        global subject
        try:
                group = subject[1].upper()
        except:
                return 'Subject: LOOKUP FAILED\n\nCheck syntax'
        results = group_lookup(group)
        if sender in results:
                return 'Subject: LOOKUP SUCCESSFUL\n\n=== RESULTS FOR '+group+'===\n'+'\n'.join(results)
        else:
                return 'Subject: LOOKUP FAILED\n\nYou must be a member of this group.'

def KICK():
        """KICK [member] FROM [group]"""
        global sender
        global subject
        if len(subject) < 3:
                return 'Subject: KICK FAILED\n\nCheck syntax'
        member = subject[1]
        group = subject[-1].upper()
        # CHECK IF REQUESTER HAS PERMISSION
        permit = False
        if group != 'ADMIN' and sender in group_lookup('ADMIN'):
                permit = True
        elif sender == group_lookup(group)[0]:
                permit = True
        if permit:
                try:
                        f = open('data/group/'+group[0]+'.txt','r+')
                except:
                        return 'Subject: KICK FAILED\n\nUnable to find group'
                while 1:
                        try:
                                struct = []
                                pt = f.tell()
                                g, e = f.readline().split()
                                if g == group:
                                        for item in e.split(','):
                                                if item != member:
                                                        struct.append(item)
                                        post = f.read()
                                        craft = g+' '+','.join(struct)
                                        f.seek(pt)
                                        f.write(craft + '\n' + post)
                                        f.truncate()
                                        f.close()
                                        break
                        except:
                                break
                return 'Subject: KICK SUCCESSFUL\n\n'+member+' is no longer a member of '+group
        else:
                return 'Subject: KICK FAILED\n\nNo permission'

def EDIT():
        """EDIT [path/file]. Overwrites a once uploaded file"""
        global sender
        global subject
        global msg
        try:
                path, fname = subject[1].split('/')
                path = path.upper()
                fname = fname.upper()
        except:
                return 'Subject: EDIT FAILED\n\nCheck syntax'
        try:
                f = open('files/'+path+'/'+fname+'.txt','r+')
        except:
                return 'Subject: EDIT FAILED\n\nUnable to open the file'
        while 1:
                try:
                        line = f.readline()
                        if line.split()[0] == 'OWNER:' and line.split()[1] == sender:
                                permit = True
                        elif line.split()[0] == 'EDIT:' and sender in group_lookup(line.split()[1]):
                                permit = True
                except:
                        break
        if permit:
                boring = True
                for line in msg.as_string().split('\n'):
                        if boring == False:
                                f.write(line+'\n')
                        elif line[:8].upper() == 'SUBJECT:':
                                boring = False
                f.truncate()
                f.close()
                return 'Subject: EDIT SUCCESSFUL\n\n'+path+'/'+fname+' Has just been edited.'
        else:
                return 'Subject: EDIT FAILED\n\nYou may not edit this file.'

def DELETE():
        """Deletes a file from a computer."""
        global sender
        global subject
        try:
                path, fname = subject[1].split('/')
                path = path.upper()
                fname = fname.upper()
        except:
                return 'Subject: DELETE FAILED\n\nCheck Syntax'
        # CHECKS IF PERMISSION TO DELETE
        permit = False
        if sender in group_lookup('ADMIN'):
                permit = True
        elif sender == group_lookup(path)[0]:
                permit = True
        else:
                f = open('files/'+path+'/'+fname+'.txt','r')
                owner = f.readline().split()[1]
                f.close()
                if sender == owner:
                        permit = True
        if permit:
                import os
                os.remove('files/'+path+'/'+fname+'.txt')
                return 'Subject: DELETE SUCCESSFUL\n\n'+path+'/'+fname+' has been deleted.'
        else:
                return 'Subject: DELETE FAILED\n\nYou are not allowed to delete this file.'

def INFO():
        """Replaces HELP. Shows command ussages, and groups the requester belongs in. if a group is given shows directory listing too."""
        global subject
        global sender
        resp = 'Subject: INFO SUCCESSFUL\n\n'
        # OUTPUT TUTORIAL LINK
        resp += '=== COMMAND USSAGE ===\nFor command ussage go to https://github.com/Eggsanity/ESA/wiki\n'
        # OUTPUT SUPPORTED COMMANDS
        resp += '=== SUPPORTED COMMANDS ===\n'
        f = open('data/cmd.txt','r')
        resp += f.read()
        f.close()
        # IF GROUP GIVEN LIST DIRECTORY
        import os
        try:
                if sender in group_lookup(subject[1].upper()):
                        resp += '=== FILES FOR '+subject[1].upper()+' ===\n'
                        for i in os.listdir('files/'+subject[1].upper()):
                                resp += i[:-4]+' , '
        except:
                pass
        return resp

def INVITE():
        """INVITE [email] TO [group]. Where [email] is the email address you wish to invite to the group. Where [group] is the group you are the supervisor of that you are inviting the user to. Invites a member to a group"""
        global subject
        global sender
        subject[1] = subject[1].lower()
        subject[-1] = subject[-1].upper()
        if len(subject) < 3:
                return 'Subject: INVITE FAILED\n\nDid not receive an email and a group name.'
        if subject[-1] == 'USER':
                if sender in group_lookup('SUPERVISOR') or sender in group_lookup('ADMIN'):
                        permit = True
                else:
                        return 'Subject: INVITE FAILED\n\nYou are not an ADMIN or a SUPERVISOR'
        elif subject[-1] in ['SUPERVISOR']:
                if sender in group_lookup('ADMIN'):
                        permit = True
                else:
                        return 'Subject: INVITE FAILED\n\nYou must be an ADMIN to invite to the ADMIN or SUPERVISOR group.'
        else:
                try:
                        if group_lookup(subject[-1])[0] == sender:
                                permit = True
                        else:
                                return 'Subject: INVITE FAILED\n\nYou do not have SUPERVISOR permissions for '+subject[-1]
                except:
                        return 'Subject: INVITE FAILED\n\nGroup does not exist.'
        if not subject[1] in group_lookup('USER') and not subject[-1] == 'USER':
                permit = False
                return 'Subject: INVITE FAILED\n\nThe user must be added to the USER group before they can be invited to other groups.'
        if permit:
                if subject[1] in group_lookup(subject[-1]):
                        return "Subject INVITE FAILED\n\n"+subject[1]+" Is already a member of "+subject[-1]
                try:
                        f = open('data/group/'+subject[-1][0].upper()+'.txt','r+')
                        while 1:
                                try:
                                        line = f.readline().split()[0]
                                        if line == subject[-1]:
                                                s = f.tell()-1
                                                f.seek(s)
                                                post = f.read()
                                                f.seek(s)
                                                f.write(','+subject[1]+post)
                                                f.close()
                                                success = True
                                except:
                                        break
                        if success:
                                return 'Subject: INVITE SUCCESSFUL\n\n'+subject[1]+' is now a member of '+subject[-1]
                        else:
                                return 'Subject: INVITE FAILED\n\nCheck group or email spelling.'
                except:
                        return 'Subject: INVITE FAILED\n\nCheck group or email spelling.'

def NEWGROUP():
        """NEWGROUP [group_name] [group_supervisor]. Creates a new group (does not asign members). Groups: ADMIN"""
        global subject
        global sender
        subject[-1] = subject[-1].lower()
        subject[1] = subject[1].upper()
        if len(subject) < 3:
                return 'Subject: NEWGROUP FAILED\n\nNeeds a group name and a group supervisor'
        if not subject[-1] in group_lookup('USER'):
        	return "Subject: NEWGROUP FAILED\n\nAssigned supervisor needs to be a known user. Add assigned group supervisor to group USER first."
        if subject[1] in ['ADMIN','SUPERVISOR','USER']:
                return "Subject: NEWGROUP FAILED\n\nYou're attempting to overwrite primary group."
        if sender in group_lookup('ADMIN'):
                # CHECK IF GROUP EXISTS
                if not len(group_lookup(subject[1])) == 0:
                        return 'Subject: NEWGROUP FAILED\n\nThis group already exists.'
                else:
                        try:
                                f = open('data/group/'+subject[1][0].upper()+'.txt','a')
                        except:
                                f = open('data/group/'+subject[1][0].upper()+'.txt','w')
                        f.write(subject[1].upper()+' '+subject[2]+'\n')
                        f.close()
                        # ADD TO SUPERVISOR
                        ret = ''
                        if not subject[-1] in group_lookup('SUPERVISOR'):
                                old = subject
                                subject = 'INVITE '+subject[-1]+' '+'SUPERVISOR'
                                subject = subject.split()
                                ret = str(INVITE())
                        try:
                                import os
                                os.mkdir("./files/"+old[1])
                        except:
                                pass
                        return 'Subject: NEWGROUP SUCCESSFUL\n\n'+old[1]+' is supervised by '+old[-1]+'\n\n'+ret
        else:
                return 'Subject: NEWGROUP FAILED\n\nThis email address is unable to create groups.'
        
def DOWNLOAD():
        """DOWNLOAD [group/file]"""
        global subject
        global sender
        global path
        permit = False
        try:
                path, fname = subject[1].split('/')
                path = path.upper()
                fname = fname.upper()
        except:
                return 'Subject: DOWNLOAD FAILED\n\nInvalid syntax.'
        if sender in group_lookup(path):
                try:
                        f = open('files/'+path+'/'+fname+'.txt','r')
                        content = f.read()
                        content = content[content.find('\n\n')+2:]
                        f.close()
                        return 'Subject: DOWNLOAD SUCCESSFUL\n'+content
                except:
                        return 'Subject: DOWNLOAD FAILED\n\nFile does not exist.'
        else:
                return 'Subject: DOWNLOAD FAILED\n\nYou do not have access to this group'
        
def UPLOAD():
        """UPLOAD [group/file_name] EDIT [group(s)]. Where [file_name] is the name of a non-existing file you wish to create. Where [group(s)] is the group permitted to interact with the created file as the word before it suggests (READ/EDIT). Creates a new file that can be saved remotely. Only the owner can delete the file. Groups with READ permissions can receive the file while groups with EDIT can edit the contents of the file. GROUPS: USER"""
        import email
        global msg
        global subject
        global sender
        try:
                path, fname = subject[1].split('/')
                path = path.upper()
                fname = fname.upper()
        except:
                return 'Subject: UPLOAD FAILED\n\nInvalid syntax'
        if len(subject) > 2:
                edit = subject[-1].upper()
        else:
                edit = ''
        if sender in group_lookup(path):
                try: # CHECK THAT FILE DOESN'T EXIST
                        f = open('files/'+path+'/'+fname+'.txt','r')
                        f.close()
                        return 'Subject: UPLOAD FAILED\n\nThe file already exists.'
                except:
                        f = open('files/'+path+'/'+fname+'.txt','w')
                        f.write('OWNER: '+sender+'\n')
                        if edit:
                                f.write('EDIT: '+ ','.join(edit.split(','))+'\n')
                        f.write('\n')
                        boring = True
                        for line in msg.as_string().split('\n'):
                                if boring == False:
                                        f.write(line+'\n')
                                elif line[:8].upper() == 'SUBJECT:':
                                        boring = False
                        f.close()
                        return 'Subject: UPLOAD WAS SUCCESSFUL\n\nFILE: '+path+'/'+fname+'\nOWNER: '+sender+'\nEDIT: '+','.join(edit.split(','))
        else:
                return "Subject: UPLOAD FAILED\n\nYou don't have permission to upload to this group"

def BASH():
        """BASH [cmd]: Where [cmd] is the command that will get passed to the system shell. GROUPS: ADMIN"""
        global subject
        resp = "Subject: Command Output\n\n"
        import subprocess
        resp += subprocess.check_output(subject[1:])
        return resp

def group_lookup(group):
        """Looksup group by name returns group members as list."""
        try:
                f = open('data/group/'+group[0].upper()+'.txt','r')
        except:
                return []
        ret = []
        for i in f:
                if i.split()[0] == group.upper():
                        ret = i.split()[1].split(',')
        f.close()
        return ret

def EXECUTE(path):
        import email
        global information
        global msg
        global subject
        global sender
        information = path
        f = open(path[1],'r')
        msg = email.message_from_string(f.read())
        sender = path[0]
        subject = str(msg['Subject']).split() # Can we remove this?
        # COMMAND CHECKING
        if subject[0] == 'INFO':#
                return INFO()
#        elif subject[0] == 'BASH': # DISABLED FOR SECURITY REASONS
#                return BASH()
        elif subject[0] == 'UPLOAD':#
                return UPLOAD()
        elif subject[0] == 'DOWNLOAD':#
                return DOWNLOAD()
        elif subject[0] == 'NEWGROUP':#
                return NEWGROUP()
        elif subject[0] == 'INVITE':#
                return INVITE()
        elif subject[0] == 'DELETE':#
                return DELETE()
        elif subject[0] == 'EDIT':#
                return EDIT()
        elif subject[0] == 'KICK':#
                return KICK()
        elif subject[0] == 'LOOKUP':#
                return LOOKUP()
        elif subject[0] == 'BROADCAST':#
                return BROADCAST()
        elif subject[0] == 'REMIND':
                return REMIND()
        elif subject[0] == 'TASKVIEW':
                return TASKVIEW()
        elif subject[0] == 'DELTASK':
                return DELTASK()
        elif subject[0] == 'DELGROUP':#
                return DELGROUP()
        # INSERT()
        # TEMPLATE()
        # APP()
