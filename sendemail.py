import sys

def main(argv, obj):
    import getopt
    global deb ;deb = False
    try:
        opts, args = getopt.getopt(argv, "l:p:f:t:s:m:a:h", ["login=", "passwd=", "from=", "to=", "subject=", "message=", "attachment=", "help", "debug"])
    except getopt.GetoptError:
        #usage()
        print "nieznane parametry"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            #usage()
            print "-l, --login	login go skrzynki email z ktorej chcemy wyslac wiadomosc"
            print "-p, --passwd	haslo do skrzynki email z ktorej chcemy wyslac wiadomosc"
            print "-f, --from	np. Imie adresata"
            print "-t, --to	adres email odbiorcy"
            print "-s, --subject	Temat wiadomosci zapisany w cudzyslowie"
            print "-m, --message	Tresc wiadomosci zapisana w cudzyslowie"
            print "-a, --attachment	zalacznik do wiadomosci"
            print "    --debug	on - aby wlaczyc, domyslnie - off"
            print "-h, --help	Pomoc"
            sys.exit()
        elif opt in ("-l", "--login"):
            obj.login = arg
        elif opt in ("-p", "--passwd"):
            obj.password = arg
        elif opt in ("-f", "--from"):
            obj.FROM = arg
        elif opt in ("-t", "--to"):
            obj.TO = arg
        elif opt in ("-s", "--subject"):
            obj.SUBJECT = arg
        elif opt in ("-m", "--message"):
            obj.MESSAGE = arg
        elif opt in ("-a", "--attachment"):
            obj.ATTACHMENT = arg
        elif opt in ("--debug"):
            deb = True

    if len(opts)<6:
        print "brak parametru" ;print opts
        sys.exit(2)

class list:
    login = ""
    password = ""
    FROM = ""
    TO = ""
    SUBJECT = ""
    MESSAGE = ""
    ATTACHMENT = ""

def send_email(obj):
    import smtplib, base64, os

    MSGB64 = base64.b64encode(obj.MESSAGE)
    ATNAME = obj.ATTACHMENT.split("/")
    ATB64 = base64.b64encode(open(obj.ATTACHMENT, 'rb').read())
    
    message = """\From: %s\nTo: %s\nSubject: %s
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="--_com.android.email_354749848945390"

----_com.android.email_354749848945390
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: base64

%s
----_com.android.email_354749848945390
Content-Type: ;
 name="attachment"
Content-Transfer-Encoding: base64
Content-Disposition: attachment;
 filename="%s";
 size=%s

%s

----_com.android.email_354749848945390--
    """ % (obj.FROM, ", ".join(obj.TO), obj.SUBJECT, MSGB64, ATNAME[len(ATNAME)-1], len(ATB64), ATB64)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) ;debug(server)
        result = server.ehlo() ;debug("ehlo - %s" % (result,))
        result = server.starttls() ;debug("starttls - %s" % (result,))
        result = server.login(obj.login, obj.password) ;debug("Login: %s\nPassword: %s\nLogowanie - %s" % (obj.login, obj.password, result,))
        result = server.sendmail(obj.FROM, obj.TO, message) ;debug("from: %s\nto: %s\nsubject: %s\nmessage: %s\nWysylanie wiadowosci - %s" % (obj.FROM, obj.TO, obj.SUBJECT, obj.MESSAGE, result,))
        result = server.close() ;debug("server.close - %s" % (result,))
        debug('wyslano')
    except:
        debug("nie udalo sie wyslac wiadomosci")

def debug(komunikat):
    if deb:
        print komunikat
    else:
        pass

l = list()
main(sys.argv[1:], l)
send_email(l)
debug("Koniec programu")

#python sendemail.py -l email@gmail.com -p haslo3 
#-f Nowak -t @wp.pl -s "Test" -m "Test" -a trayicon.ico --debug
