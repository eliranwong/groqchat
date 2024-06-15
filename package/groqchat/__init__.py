from groqchat import config
from groq import Groq
from prompt_toolkit import print_formatted_text, HTML
from pathlib import Path
import pprint, os, shutil, textwrap, wcwidth, requests, sys, subprocess, re, platform, psutil
import speech_recognition as sr
import sounddevice, soundfile

thisFile = os.path.realpath(__file__)
config.packageFolder = os.path.dirname(thisFile)
if config.developer:
    print(f"Package located at: {config.packageFolder}")
config.localStorage = os.path.expanduser("~")

config.isPipUpdated = False
thisPlatform = platform.system()
config.thisPlatform = "macOS" if thisPlatform == "Darwin" else thisPlatform

config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False

userFolder = os.path.join(config.localStorage, "gchat")
Path(userFolder).mkdir(parents=True, exist_ok=True)
userFolder = os.path.join(config.localStorage, "gchat", "LLMs", "piper")
Path(userFolder).mkdir(parents=True, exist_ok=True)

def checkPyaudio():
    try:
        import sounddevice
        import speech_recognition as sr
        mic = sr.Microphone() 
        del mic
        config.pyaudioInstalled = True
    except:
        if config.isTermux:
            config.pyaudioInstalled = False
            #print2("Installing 'portaudio' and 'Pyaudio' ...")
            #os.system("pkg install portaudio")
            #config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
        elif isCommandInstalled("brew"):
            print2("Installing 'portaudio' and 'Pyaudio' ...")
            os.system("brew install portaudio")
            config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
        elif isCommandInstalled("apt"):
            print2("Installing 'portaudio19-dev' and 'Pyaudio' ...")
            os.system("sudo apt update && sudo apt install portaudio19-dev")
            config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
        elif isCommandInstalled("dnf"):
            print2("Installing 'portaudio-devel' and 'Pyaudio' ...")
            os.system("sudo dnf update && sudo dnf install portaudio-devel")
            config.pyaudioInstalled = True if installPipPackage("--upgrade PyAudio") else False
        else:
            config.pyaudioInstalled = False

    if not config.pyaudioInstalled and not config.isTermux:
        print3("Note: 'pyAudio' is not installed.")
        print1("It is essential for built-in voice recognition feature.")

def playAudio(audioFile):
    sounddevice.play(*soundfile.read(audioFile)) 
    sounddevice.wait()

def voiceTyping():
    # reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
    # import sounddevice to solve alsa error display: https://github.com/Uberi/speech_recognition/issues/182#issuecomment-1426939447
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if config.voiceTypingNotification:
            playAudio(os.path.join(config.packageFolder, "audio", "notification1_mild.mp3"))
        #run_in_terminal(lambda: print2("Listensing to your voice ..."))
        if config.voiceTypingAdjustAmbientNoise:
            r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    if config.voiceTypingNotification:
        playAudio(os.path.join(config.packageFolder, "audio", "notification2_mild.mp3"))
    #run_in_terminal(lambda: print2("Processing to your voice ..."))
    if config.voiceTypingPlatform == "google":
        # recognize speech using Google Speech Recognition
        try:
            # check google.recognize_legacy in SpeechRecognition package
            # check available languages at: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            # config.voiceTypingLanguage should be code list in column BCP-47 at https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            return r.recognize_google(audio, language=config.voiceTypingLanguage)
        except sr.UnknownValueError:
            #return "[Speech unrecognized!]"
            return ""
        except sr.RequestError as e:
            return "[Error: {0}]".format(e)
    elif config.voiceTypingPlatform == "googlecloud" and os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Speech-to-Text" in config.enabledGoogleAPIs:
        # recognize speech using Google Cloud Speech
        try:
            # check availabl languages at: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            # config.voiceTypingLanguage should be code list in column BCP-47 at https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            return r.recognize_google_cloud(audio, language=config.voiceTypingLanguage, credentials_json=config.google_cloud_credentials)
        except sr.UnknownValueError:
            #return "[Speech unrecognized!]"
            return ""
        except sr.RequestError as e:
            return "[Error: {0}]".format(e)
    elif config.voiceTypingPlatform == "whisper":
        # recognize speech using whisper
        try:
            # check availabl languages at: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
            # config.voiceTypingLanguage should be uncapitalized full language name like "english" or "chinese"
            return r.recognize_whisper(audio, model=config.voiceTypingWhisperEnglishModel if config.voiceTypingLanguage == "english" else "large", language=config.voiceTypingLanguage)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return "[Error]"
    elif config.voiceTypingPlatform == "whispercpp":
        #from speech_recognition.audio import AudioData
        #assert isinstance(audio, AudioData), "Data must be audio data"
        wav_bytes_data = audio.get_wav_data(
            convert_rate=16000,  # audio samples must be 8kHz or 16 kHz
            convert_width=2  # audio samples should be 16-bit
        )
        wav_file = os.path.join(config.packageFolder, "temp", "voice.wav")
        with open(wav_file, "wb") as fileObj:
            fileObj.write(wav_bytes_data)
        # Example of cli: ./main -np -nt -l auto -t 12 -m ggml-large-v3-q5_0.bin -f ~/Desktop/voice.wav
        # *.bin model files available at: https://huggingface.co/ggerganov/whisper.cpp/tree/main
        if not os.path.isfile(config.whispercpp_main) or not os.path.isfile(config.whispercpp_model):
            return "[Error]"
        cli = f'''"{config.whispercpp_main}" -np -nt -l {'en' if config.voiceTypingLanguage.lower() in ('english', 'en') else 'auto'} -t {getCpuThreads()} -m "{config.whispercpp_model}" -f "{wav_file}" {config.whispercpp_additional_options}'''
        process = subprocess.Popen(cli.rstrip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return "[Error]" if stderr and not stdout else stdout.decode("utf-8").strip()

def getCpuThreads():
    if config.cpu_threads and isinstance(config.cpu_threads, int):
        return config.cpu_threads
    physical_cpu_core = psutil.cpu_count(logical=False)
    return physical_cpu_core if physical_cpu_core and physical_cpu_core > 1 else 1

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
        'pyaudioInstalled',
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