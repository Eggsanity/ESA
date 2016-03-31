import getpass
while 1:
    print(chr(27) + "[2J")
    print("You are running the setup script for ESA.")
    print("This will setup the required configuration to get you started.\nAfter which you can do all further configuration through ESA.")
    print("\nYou should connect an UNUSED/NON-PERSONAL email address for ESA.")
    print("ESA automatically deletes emails after it finishes reading them.\nUsing your personal email with ESA will delete all your emails\nbefore you get a chance to read them.\n")
    print("If attaching ESA to a gmail account, less information is required. Otherwise you need to know your IMAP and SMTP server addresses/ports.")
    while 1:
        ans = raw_input("Are you connecting ESA to a gmail account?[y/n]: ")
        if ans.upper() == 'Y': # GMAIL INFO
            imapsrv = 'imap.gmail.com'
            smtpsrv = 'smtp.gmail.com:587'
            print("\nYou selected gmail. Make sure you have a gmail account reserved for ESA before continuing")
            while 1:
                print("The information requested should be for the email address ESA connects to (NOT YOUR PERSONAL EMAIL)")
                user = raw_input("ENTER FULL USER EMAIL ADDRESS: ")
                print("Enter your password. (Characters will not show on the screen)")
                pword = getpass.getpass()
                print("User address: "+user)
                print("Pass Length: "+str(len(pword)))
                done = raw_input("Is this correct? [y] to continue. [n] to try again. [y/n]: ")
                if done.upper() == 'Y':
                    break
                print("Starting over...")
            break
        elif ans.upper() == 'N':
            while 1:
                print("\nThe information requested should be for the email address ESA connects to (NOT YOUR PERSONAL EMAIL)")
                imapsrv = raw_input("ENTER IMAP SERVER ADDRESS: ")
                smtpsrv = raw_input("ENTER SMTP SERVER ADDRESS: ")
                user = raw_input("ENTER USER EMAIL ADDRESS: ")
                print("Enter your password. (Characters will not show on the screen)")
                pword = getpass.getpass()
                print("User address: "+user)
                print("Pass Length: "+str(len(pword)))
                done = raw_input("Is this correct? [y] to continue. [n] to try again. [y/n]: ")
                if done.upper() == 'Y':
                    break
                print("Starting over...")
            break
        print("INVALID ANSWER. ENTER EITHER 'Y' or 'N'")
    print("\nAdd a SUPER ADMIN. Add an email address for a user that should be allowed to administer ESA. Further configurations will be done with this email.")
    print("ESA will be able to communicate with this email address but will not have any further access. This can be a personal/work email address.")
    admin = raw_input("ADMIN EMAIL: ")

    print('\n\n** ESA **')
    print('USER EMAIL: ' + user)
    print('PASS LENGTH: ' + str(len(pword)))
    print('IMAP: ' +imapsrv)
    print('SMTP: ' +smtpsrv)
    print("\n** ADMIN **")
    print('EMAIL: ' +admin)

    done = raw_input("\n\nDone? [y] finalize configuration. [n] start over. [y/n]")
    if done.upper() == 'Y':
        try:
            f = open('data/config.txt','w')
            f.write('IMAPSRV '+imapsrv+'\n')
            f.write('EMAILADDR '+user+'\n')
            f.write('SMTPSRV '+smtpsrv+'\n')
            f.write('REFRESH 40'+'\n')
            f.write('PASSWORD '+pword+'\n')
            f.close()
            f = open('data/group/A.txt','w')
            f.write('ADMIN '+admin+'\n')
            f.close()
            f = open('data/group/S.txt','w')
            f.write('SUPERVISOR '+admin+'\n')
            f.close()
            f = open('data/group/U.txt','w')
            f.write('USER '+admin+'\n')
        except:
            print("Something went wrong... Please confirm the application is in a fresh/untampered state.")
        print("SETUP COMPLETED")
        break
