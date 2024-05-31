from groqchat import config
from groq import Groq
from prompt_toolkit import print_formatted_text, HTML

import pprint, os, shutil, textwrap, wcwidth

thisFile = os.path.realpath(__file__)
config.packageFolder = os.path.dirname(thisFile)
config.localStorage = os.path.expanduser("~")

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

def saveConfig():
    temporaryConfigs = ['new_chat_response', 'localStorage', 'packageFolder', 'tempChunk', 'selectAll', 'pagerContent']
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