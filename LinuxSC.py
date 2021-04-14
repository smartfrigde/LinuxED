#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# written by Creatable/ modified by fridge

# credits:
# - Tcll5850: https://gitlab.com/Tcll
#   for cleaning up the code, making it more maintainable, and extending it's functionality, as well as fixing issues with older python versions.

import os
import sys
import urllib.request
import zipfile
import distutils.core
import shutil
import getpass
import tempfile
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR

if __name__ == "__main__":
    """Comment out old Windows notice
    if os.name == 'nt': print('WARNING: it appears you are running the Linux installer on Windows.\n'
                            'If you are unaware of what you\'re doing, it\'s recommended you close this installer.\n'
                            'Otherwise you may continue at your own risk.\n')"""

    if os.name == 'nt': print('WARNING: it appears you are running LinuxSC on Windows.\n'
                            'LinuxSC was not originally made for Windows and Windows compatibility is not maintained.\n'
                            'Continue at your own risk.')
    # Define the starting variables, these are all their own thing.
    username = getpass.getuser()
    dirpath = os.path.realpath('')
    currentdir = True
    if 'XDG_DATA_HOME' in os.environ:
        if os.path.exists(os.path.join(os.environ['XDG_DATA_HOME'], "SmartCord")):
            dirpath = os.environ['XDG_DATA_HOME']
            currentdir = False
    elif 'HOME' in os.environ:
         if os.path.exists(os.path.join(os.environ['HOME'], '.local', 'share', "SmartCord")):
            dirpath = os.path.join(os.environ['HOME'], '.local', 'share')
            currentdir = False
    filepath = os.path.dirname(os.path.realpath(__file__))
    tempdir = tempfile.gettempdir()
    scriptname = os.path.basename(__file__)

    detect_versions = lambda discordpath,idxsubpath: [
        (discordpath+vsn+idxsubpath, vsn) for vsn in (os.listdir(discordpath) if os.path.exists(discordpath) else []) if os.path.isdir(discordpath+vsn) and len(vsn.split('.')) == 3 ]

    print('Welcome to the LinuxSC installation script.')

    baseclients = {
        "STABLE" : detect_versions('/home/%s/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "CANARY" : detect_versions('/home/%s/.config/discordcanary/'%username, '/modules/discord_desktop_core/index.js'),
        "PTB"    : detect_versions('/home/%s/.config/discordptb/'%username, '/modules/discord_desktop_core/index.js'),
        "SNAP"   : detect_versions('/home/%s/snap/discord/current/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "FLATPAK": detect_versions('/home/%s/.var/app/com.discordapp.Discord/config/discord/'%username, '/modules/discord_desktop_core/index.js')
    }

    if sys.platform == 'darwin':
        baseclients = {
        "STABLE" : detect_versions('/Users/%s/Library/Application Support/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "CANARY" : detect_versions('/Users/%s/Library/Application Support/discordcanary/'%username, '/modules/discord_desktop_core/index.js'),
        "PTB"    : detect_versions('/Users/%s/Library/Application Support/discordptb/'%username, '/modules/discord_desktop_core/index.js')
    }
    elif os.name == 'nt':
        baseclients = {
            "STABLE" : detect_versions('C:/Users/%s/AppData/Roaming/Discord/'%username, '/modules/discord_desktop_core/index.js'),
            "CANARY" : detect_versions('C:/Users/%s/AppData/Roaming/discordcanary/'%username, '/modules/discord_desktop_core/index.js'),
            "PTB"    : detect_versions('C:/Users/%s/AppData/Roaming/Discord PTB/'%username, '/modules/discord_desktop_core/index.js')
        }

    clients = [ (str(i+1),cpv) for i,cpv in enumerate( (c,p,v) for c in baseclients if baseclients[c] for p,v in baseclients[c] ) ]
    clients.append( (str(len(clients)+1), ("CUSTOM",'', '')) )
    getclient = dict(clients).get

    def validate_custom_client():
        while True:
            print("\nPlease enter the location of your client's index.js file.")
            jspath = input('> ')
            if os.path.exists(jspath) and os.path.isfile(jspath): return 'CUSTOM', jspath, ''
            elif not jspath:
                print("\nOperation cancelled...")
                return 'CUSTOM', jspath, ''
            else:
                print("\nError: The specified location was not valid.")
                print("Please enter a valid location or press Enter to cancel.")

    def select_client(allow_custom=False):
        if len(clients) > 2 or allow_custom:
            while True:
                print('\nPlease enter the number for the client you wish to patch, or press Enter to exit:')
                result = input('%s\n> '%('\n'.join('%s. %s: %s'%(i,o,v) for i,(o,p,v) in clients)) )
                client, jspath, version = getclient( result, (None,'','') )
                if client=='CUSTOM':
                    client, jspath, version = validate_custom_client()
                    if not jspath: continue
                if jspath: return client, jspath, version
                if not result:
                    print("\nOperation cancelled...")
                    #input('Press Enter to Exit...')
                    return 'CUSTOM', jspath, ''
                print("\nError: The specified option was not valid.")
        
        elif len(clients) == 1:
            print('\nThe installer could not detect any known Discord clients.')
            print('Do you have Discord installed in a custom location? (y/n)')
            if input("> ").upper() in {"Y","YES"}: return validate_custom_client()
            else:
                print('\nNo Discord client could be found.')
                print('Please install Discord and re-run this installer.')
                #input('Press Enter to Exit...')
                return 'CUSTOM', '', ''
        
        else: return getclient('1')

    client, jspath, version = select_client()
    if jspath:
        backuppath = "%s.backup"%jspath
        while True:
            print('\nOperating on client: %s %s\n'%(client,version))
            print('Please type the number for your desired option:')
            enhanceddir = os.path.join(dirpath, "SmartCord")
            if os.name == 'nt':
                injdir = 'process.env.injDir = "%s"' % enhanceddir.encode('unicode_escape').decode("utf-8")
            else:
                injdir = 'process.env.injDir = "%s"' % enhanceddir

            # this is not my code but it's what I put at the end of index.js
            patch = """%s
            require(`${process.env.injDir}/injection.js`);
            module.exports = require('./core.asar');"""%injdir

            # room for expansion (other params can be provided here)
            optionsdict = [('Install SC',),('Uninstall SC',),('Update SC',),('Update LinuxSC',),('Select Client',)]
            if currentdir == False:
                optionsdict.append(('Use current directory',))
            else:
                if 'XDG_DATA_HOME' in os.environ:
                    optionsdict.append(('Use $XDG_DATA_HOME',))
                if 'HOME' in os.environ:
                    optionsdict.append(('Use $HOME',))
            optionsdict.append(('Exit',))
            options = [ (str(i+1),o) for i,o in enumerate(optionsdict)]
            getoption = dict(options).get

            option,*params = getoption( input( '%s\n> '%('\n'.join('%s. %s'%(i,o) for i,(o,*p) in options) ) ), (None,) )
            print()
            
            if option == 'Exit':
                print("Exiting...")
                exit()
                break # shouldn't get here, but just in case.
            
            
            elif option == 'Update LinuxSC':
                print("Updating LinuxSC...")
                urllib.request.urlretrieve('https://github.com/smartfrigde/LinuxSC/archive/master.zip', '%s/LinuxSCUpdate.zip' % tempdir)
                with zipfile.ZipFile("%s/LinuxSCUpdate.zip" % tempdir,"r") as zip_ref:
                    zip_ref.extractall(tempdir)
                os.remove("%s/LinuxSC-master/LICENSE" % tempdir)
                os.remove("%s/LinuxSC-master/README.md" % tempdir)
                os.remove("%s/LinuxSC-master/.gitignore" % tempdir)
                shutil.move("%s/LinuxSC-master/LinuxSC.py" % tempdir, "%s/LinuxSC-master/%s" % (tempdir, scriptname))
                distutils.dir_util.copy_tree('%s/LinuxSC-master/' % tempdir, filepath)
                shutil.rmtree("%s/LinuxSC-master" % tempdir)
                os.remove("%s/LinuxSCUpdate.zip" % tempdir)
                if os.name != "nt":
                    try:
                        os.system("chmod +x %s" % os.path.join(filepath, scriptname))
                    except:
                        print("Couldn't make script executable...\nYou may experience problems when trying to use it again")
                print("Update complete!\nPlease restart LinuxSC for the update to take effect.")
        
        
            elif option == 'Uninstall SC':
                print('Uninstalling SmartCord...')
                if os.path.exists(backuppath):
                    print("Making sure index.js is no longer read only before removing it...")
                    os.chmod(jspath, S_IWUSR|S_IREAD)
                    os.remove(jspath)
                    shutil.move(backuppath, jspath)
                    print("Successfully uninstalled SmartCord!")
                else:
                    print("Error: Couldn't find index.js backup, did you use the installer to install ED?\n")
        
            elif option == 'Install SC':
                if not os.path.exists(enhanceddir):
                    print("Downloading SC...")
                    urllib.request.urlretrieve('https://github.com/smartfrigde/smartcord/archive/main.zip', '%s/SmartCord.zip' % tempdir)
                    with zipfile.ZipFile("%s/SmartCord.zip" % tempdir,"r") as zip_ref:
                        zip_ref.extractall(tempdir)
                    shutil.move("%s/smartcord-main" % tempdir, "%s/SmartCord" % dirpath)
                    os.remove("%s/SmartCord.zip" % tempdir)
                
                if not os.path.exists(backuppath):
                    print("Creating index.js.backup...")
                    with open(jspath,'r') as original:
                        with open(backuppath,'w') as backup: backup.write(original.read())
        
                print("Patching index.js...")
                with open(jspath,"w") as idx: idx.write(patch)

                print("Making index.js read only so Discord can't tamper with it...")
                os.chmod(jspath, S_IREAD|S_IRGRP|S_IROTH)

                cfgpath = "%s/config.json"%enhanceddir
                if not os.path.exists(cfgpath):
                    print("Creating config.json...")
                    with open(cfgpath,"w") as cfg: cfg.write("{}")
            
                print("SmartCord installation complete!\n")

            elif option == 'Update SC':
                if os.path.exists(enhanceddir):
                    print("Updating SC...")
                    urllib.request.urlretrieve('https://github.com/smartfrigde/smartcord/archive/main.zip', '%s/SCUpdate.zip' % tempdir)
                    with zipfile.ZipFile("%s/SCUpdate.zip" % tempdir,"r") as zip_ref:
                        zip_ref.extractall(tempdir)
                    distutils.dir_util.copy_tree('%s/smartcord-main' % tempdir, '%s/SmartCord' % dirpath)
                    shutil.rmtree("%s/smartcord-main" % tempdir)
                    os.remove("%s/SCUpdate.zip" % tempdir)
                    print("Update complete!")
                else:
                    print("It seems SmartCord is not installed in the current directory so it was unable to be updated.")
            elif option == 'Select Client':
                print("Selecting new Discord client...")
                backup = (client, jspath, version)
                client, jspath, version = select_client(True)
                if not jspath: client, jspath, version = backup
                print('\nOperating on client: %s %s\n'%(client,version))
            elif option == 'Use current directory':
                dirpath = os.path.realpath('')
                currentdir = True
            elif option == 'Use $XDG_DATA_HOME':
                dirpath = os.environ['XDG_DATA_HOME']
                currentdir = False
            elif option == 'Use $HOME':
                dirpath = os.path.join(os.environ['HOME'], '.local', 'share')
                currentdir = False

            else:
                print('Error: The specified option was not valid.\n')
            print('Please type the number for your desired option:')
