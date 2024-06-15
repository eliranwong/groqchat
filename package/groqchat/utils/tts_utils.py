from groqchat import config, downloadFile, installPipPackage, getHideOutputSuffix, print2
import os, traceback, sounddevice, soundfile, pydoc, shutil


class TTSUtil:

    @staticmethod
    def play(content):
        if config.tts and content.strip():
            try:
                if shutil.which("termux-tts-speak"):
                    # Use termux-tts-speak via termux API on Android
                    # read https://wiki.termux.com/wiki/Termux-tts-speak
                    additional_options = f" {config.termuxtts_additional_options.strip()}" if config.termuxtts_additional_options.strip() else ""
                    voice = f" -l {config.termuxtts_voice.strip()}" if config.termuxtts_voice.strip() else ""
                    cmd = f"termux-tts-speak -r {config.vlcSpeed}{voice}{additional_options}"
                    pydoc.pipepager(content, cmd=cmd)
                elif config.thisPlatform == "macOS":
                    additional_options = f" {config.say_additional_options.strip()}" if config.say_additional_options.strip() else ""
                    voice = f" -v {config.say_voice.strip()}" if config.say_voice.strip() else ""
                    cmd = f"say -r {config.say_speed}{voice}{additional_options}"
                    pydoc.pipepager(content, cmd=cmd)
                elif config.thisPlatform == "Windows":

                    homeWsay = os.path.join(config.localStorage, "gchat", "wsay.exe")
                    isWsayFound = (shutil.which("wsay") or os.path.isfile(homeWsay))
                    if not isWsayFound:
                        print2("Downloading 'wsay.exe' ...")
                        downloadFile("https://github.com/p-groarke/wsay/releases/download/1.6.2/wsay.exe", homeWsay)
                        isWsayFound = (shutil.which("wsay") or os.path.isfile(homeWsay))
                        print2(f"Saved in: {homeWsay}")

                    additional_options = f" {config.wsay_additional_options.strip()}" if config.wsay_additional_options.strip() else ""
                    cmd = f'''"{homeWsay if os.path.isfile(homeWsay) else 'wsay'}" --voice {config.wsay_voice} --speed {config.wsay_speed}{additional_options}'''
                    pydoc.pipepager(content, cmd=cmd)
                elif config.thisPlatform == "Linux" and not config.isTermux:
                    if not shutil.which("piper"):
                        install = installPipPackage("piper-tts")
                        if not install:
                            return None
                    audioFile = os.path.join(config.packageFolder, "temp", "piper.wav")
                    model_dir = os.path.join(config.localStorage, "gchat", "LLMs", "piper")
                    model_path = f"""{os.path.join(model_dir, config.piper_voice)}.onnx"""
                    model_config_path = f"""{model_path}.json"""
                    piper_additional_options = f" {config.piper_additional_options.strip()}" if config.piper_additional_options.strip() else ""
                    if os.path.isfile(model_path):
                        if shutil.which("cvlc"):
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
                        elif shutil.which("aplay"):
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
                        else:
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
                    else:
                        print2("[Downloading voice ...] ")
                        if shutil.which("cvlc"):
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
                        elif shutil.which("aplay"):
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
                        else:
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
                    pydoc.pipepager(content, cmd=cmd)
                    if not shutil.which("cvlc") and not shutil.which("aplay"):
                        TTSUtil.playAudioFile(audioFile)
            except:
                if config.developer:
                    print(traceback.format_exc())
                else:
                    pass

    @staticmethod
    def playAudioFile(audioFile):
        sounddevice.play(*soundfile.read(audioFile)) 
        sounddevice.wait()
