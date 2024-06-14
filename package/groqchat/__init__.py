from groqchat import config
from groq import Groq
from prompt_toolkit import print_formatted_text, HTML

import pprint, os, shutil, textwrap, wcwidth, requests, sys, subprocess, re, platform

thisFile = os.path.realpath(__file__)
config.packageFolder = os.path.dirname(thisFile)
config.localStorage = os.path.expanduser("~")

config.isPipUpdated = False
thisPlatform = platform.system()
config.thisPlatform = "macOS" if thisPlatform == "Darwin" else thisPlatform

def getStringWidth(text):
    width = 0
    for character in text:
        width += wcwidth.wcwidth(character)
    return width

def wrapText(content, terminal_width=None):
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns
    return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

def print1(content):
    if config.wrapWords:
        # wrap words to fit terminal width
        terminal_width = shutil.get_terminal_size().columns
        print(wrapText(content, terminal_width))
    else:
        print(content)

def print2(content):
    print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))

def print3(content):
    splittedContent = content.split(": ", 1)
    if len(splittedContent) == 2:
        key, value = splittedContent
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
    else:
        print2(splittedContent)

def getHideOutputSuffix():
    return f" > {'nul' if config.thisPlatform == 'Windows' else '/dev/null'} 2>&1"

def downloadFile(url, localpath, timeout=60):
    response = requests.get(url, timeout=timeout)
    with open(localpath, 'wb') as fileObj:
        fileObj.write(response.content)

def isCommandInstalled(package):
    return True if shutil.which(package.split(" ", 1)[0]) else False

def installPipPackage(module, update=True):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    if isCommandInstalled("pip"):
        pipInstallCommand = f"{sys.executable} -m pip install"

        if update:
            if not config.isPipUpdated:
                pipFailedUpdated = "pip tool failed to be updated!"
                try:
                    # Update pip tool in case it is too old
                    updatePip = subprocess.Popen(f"{pipInstallCommand} --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    *_, stderr = updatePip.communicate()
                    if not stderr:
                        print("pip tool updated!")
                    else:
                        print(pipFailedUpdated)
                except:
                    print(pipFailedUpdated)
                config.isPipUpdated = True
        try:
            upgrade = (module.startswith("-U ") or module.startswith("--upgrade "))
            if upgrade:
                moduleName = re.sub("^[^ ]+? (.+?)$", r"\1", module)
            else:
                moduleName = module
            print(f"{'Upgrading' if upgrade else 'Installing'} '{moduleName}' ...")
            installNewModule = subprocess.Popen(f"{pipInstallCommand} {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = installNewModule.communicate()
            if not stderr:
                print(f"Package '{moduleName}' {'upgraded' if upgrade else 'installed'}!")
            else:
                print(f"Failed {'upgrading' if upgrade else 'installing'} package '{moduleName}'!")
                if config.developer:
                    print(stderr)
            return True
        except:
            return False

    else:
        print("pip command is not found!")
        return False

def saveConfig():
    temporaryConfigs = [
        'new_chat_response', 
        'localStorage', 
        'packageFolder', 
        'tempChunk', 
        'selectAll', 
        'pagerContent', 
        'tempChunk', 
        'ttsPlatform', 
        'isPipUpdated',
        'thisPlatform',
    ]
    excludeConfigList = []
    configFile = os.path.join(config.packageFolder, "config.py")
    with open(configFile, "w", encoding="utf-8") as fileObj:
        for name in dir(config):
            excludeConfigList = temporaryConfigs + excludeConfigList
            if not name.startswith("__") and not name in excludeConfigList:
                try:
                    value = eval(f"config.{name}")
                    if not callable(value) and not str(value).startswith("<"):
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                except:
                    pass

def getGroqApi_key():
    '''
    support multiple grop api keys to work around rate limit
    User can manually edit config to change the value of config.groqApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.groqApi_key:
        if isinstance(config.groqApi_key, str):
            return config.groqApi_key
        elif isinstance(config.groqApi_key, list):
            if len(config.groqApi_key) > 1:
                # rotate multiple api keys
                config.groqApi_key = config.groqApi_key[1:] + [config.groqApi_key[0]]
            return config.groqApi_key[0]
        else:
            return ""
    else:
        return ""

def getGroqClient():
    return Groq(api_key=getGroqApi_key())