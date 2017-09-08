
import keyring
from Tkinter import *

def pw_service_name(host):
    return host


def prompt_for_pw(host, user):
    # Ask user for password (& save to keyring)
    root = Tk()
    pwdbox = Entry(root, show='*')

    def onpwdentry(evt):
        pw = pwdbox.get()
        keyring.set_password(pw_service_name(host), user, pw)
        root.destroy()

    def onokclick():
        pw = pwdbox.get()
        keyring.set_password(pw_service_name(host), user, pw)
        root.destroy()

    Label(root, text='Password for %s@%s' % (user, host)).pack(side='top')

    pwdbox.pack(side='top')
    pwdbox.bind('<Return>', onpwdentry)
    Button(root, command=onokclick, text='OK').pack(side='top')

    # Run tk and wait for input
    root.mainloop()

    return keyring.get_password(pw_service_name(host), user)


def forget_pw(host, user):
    keyring.delete_password(pw_service_name(host), user)


def get_password(host, user):
    # Retrieve from OS keyring
    pw = keyring.get_password(pw_service_name(host), user)

    if pw is None:
        pw = prompt_for_pw(host, user)

    return pw