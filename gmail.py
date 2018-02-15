# -*- coding: utf-8 -*-

import imaplib
import email
import os, sys
from email.header import decode_header
from re import findall
import subprocess
import json

def main(argv):
    import getopt
    global detach_dir ;detach_dir = '.'
    global deb ;deb = False
    global login ;login = ""
    global password ;password = ""

    try:
        opts, args = getopt.getopt(argv, "l:p:d:h", ["login=", "passwd=", "dir=", "help", "debug"])
    except getopt.GetoptError:
        #usage()
        print "nieznane parametry"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "-l, --login     login go skrzynki email"
            print "-p, --passwd    haslo do skrzynki email"
            print "-d, --dir       katalog do zapisu zalacznika, domyslny - ."
            print "    --debug     debugowanie włączone"
            print "-h, --help      Pomoc"
            sys.exit()
        elif opt in ("-l", "--login"):
            login = arg
        elif opt in ("-p", "--passwd"):
            password = arg
        elif opt in ("-d", "--dir"):
            detach_dir = arg
        elif opt in ("--debug"):
            deb = True

def getheader(header_text, default="ascii"):
    headers = decode_header(header_text)
    header_sections = [unicode(text, charset or default) for text, charset in headers]
    return u"".join(header_sections)

def debug(komunikat):
    if deb:
        print komunikat
    else:
        pass

main(sys.argv[1:])
jlist = ''

try:
    M = imaplib.IMAP4_SSL('imap.gmail.com') ;debug(M)
    result = M.login(login, password) ;debug("login: %s\npassword: %s\nLogowanie - %s" % (login, password, result))
    result = M.select() ;debug("select - %s" % (result,))
    result, data = M.uid('search', None, 'ALL') ;debug("Szukanie wiadomosci - %s" % (result))
    debug("Znaleziono: %s" % (data))
except:
    print ("Błąd logowania")
    sys.exit(2)
for num in data[0].split():
    result, data = M.uid('fetch', num, '(RFC822)') ;debug("Pobieranie meila nr:UID %s - %s" % (num,result))
    mail =  email.message_from_string(data[0][1])

    debug("Temat: "+mail["Subject"]) ;debug("From: "+getheader(mail["From"])) ;debug(mail["\n\n"])
    debug("Probuje wykonac: "+mail["Subject"])
    wynik = subprocess.call(mail["Subject"], shell=True) ;debug("\t(wynik:%s)"%(wynik))
    filename = ""
    for part in mail.walk():
        debug(part.get_content_maintype())
        if part.get_content_maintype() == 'multipart':
	    continue
        if part.get_content_maintype() == 'text':
            message =  part.get_payload(decode=True)
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        counter = 1
        if not filename:
            continue
            #filename = 'part-%03d%s' % (counter, 'bin')
            #counter += 1
        att_path = os.path.join(detach_dir, getheader(filename))
        if not os.path.isfile(att_path):
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
        debug('    Zaloncznik: %s' % (getheader(filename)))
    debug(message,) ;debug(filename) ;debug(mail["Subject"]) ;debug(getheader(mail["From"])) ;debug(mail["To"])
    jlist+="".join(json.dumps({"from":getheader(mail["From"]),"to":mail["To"],"subject":mail["Subject"],"message":message,"attachment":filename}))
    if wynik == 0:
        result = M.uid('COPY', num, 'wykonane') ;debug("Kopiuje wiadomosc UID %s do wykonane - %s" % (num, result,))
        if result[0] == 'OK':
            mov, data = M.uid('STORE', num , '+FLAGS', '(\Deleted)') ;debug("Usuwam wiadomosc UID:%s - %s" % (num, mov))
            #m.expunge()
    else:
        #mov, data = M.uid('STORE', num , '+FLAGS', '(\Deleted)')
        result = M.uid('COPY', num,"[Gmail]/Kosz") ;debug("Kopiuje wiadomosc UID:%s do Kosz - %s" % (num, result,))
        if result[0] == 'OK':
            mov, data = M.uid('STORE', num , '+FLAGS', '(\Deleted)') ;debug("Usuwam wiadomosc UID:%s - %s" % (num, mov))
            #m.expunge()

M.close() ;debug("close")
M.logout() ;debug("logout\nKoniec programu")

if jlist:
    print jlist

#python gmail.py -l email@gmail.com -p haslo --debug
