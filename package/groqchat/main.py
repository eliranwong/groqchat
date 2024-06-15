from groqchat import config
from groqchat import print1, print2, print3, getGroqClient, saveConfig, checkPyaudio
from groqchat.utils.streaming_word_wrapper import StreamingWordWrapper
from groqchat.utils.terminal_mode_dialogs import TerminalModeDialogs
from groqchat.utils.single_prompt import SinglePrompt
from groqchat.utils.promptValidator import FloatValidator, NumberValidator
#from groqchat.utils.tool_plugins import Plugins

from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.application import run_in_terminal
import threading, argparse, os, traceback
from prompt_toolkit.key_binding import KeyBindings


class GroqChatbot:
    """
    A simple Groq chatbot, without function calling.
    It is created for use with 3rd-party applications.
    """

    def __init__(self, name="Groq Chatbot", temperature=config.llmTemperature, max_output_tokens=config.groqApi_max_tokens):
        self.name, self.temperature, self.max_output_tokens = name, temperature, max_output_tokens
        self.messages = self.resetMessages()
        #if hasattr(config, "currentMessages") and config.currentMessages:
        #    self.messages += config.currentMessages[:-1]
        self.defaultPrompt = ""
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        if not self.temperature == config.llmTemperature:
            config.llmTemperature = self.temperature
            saveConfig()
        if not self.max_output_tokens == config.groqApi_max_tokens:
            config.groqApi_max_tokens = self.max_output_tokens
            saveConfig()
        if not config.groqApi_key:
            self.changeGroqApi()
            self.setLlmModel_groq()
        # initial check
        checkPyaudio()

    def resetMessages(self):
        return [{"role": "system", "content": config.systemMessage_groq},]

    def changeGroqApi(self):
        print3("# Groq Cloud API Key: allows access to Groq Cloud hosted LLMs")
        print1("To set up Groq Cloud API Key, read:\nhttps://github.com/eliranwong/freegenius/wiki/Set-up-a-Groq-Cloud-API-Key\n")
        print1("Enter a single or a list of multiple Groq Cloud API Key(s):")
        print()
        apikey = SinglePrompt.run(style=self.promptStyle, default=str(config.groqApi_key), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.groqApi_key = eval(apikey)
            except:
                config.groqApi_key = apikey
        saveConfig()
        print2("Configurations updated!")

    def setTemperature(self):
        print1("Enter a value between 0.0 and 2.0:")
        print1("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
        temperature = SinglePrompt.run(style=self.promptStyle, validator=FloatValidator(), default=str(config.llmTemperature))
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.llmTemperature = round(temperature, 1)
            saveConfig()
            print3(f"LLM Temperature: {temperature}")

    def setLlmModel_groq(self):
        model = TerminalModeDialogs(self).getValidOptions(
            options=(
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "llama3-8b-8192",
                "llama3-70b-8192",
            ),
            title="Groq Model",
            default=config.groqApi_chat_model,
            text="Select a model:",
        )
        if model:
            config.groqApi_chat_model = model
            print3(f"Groq model: {model}")
        saveConfig()

    def setMaxTokens(self):
        print1("Please specify maximum output tokens below:")
        if config.llmInterface == "gemini":
            default = config.geminipro_max_output_tokens
        elif config.llmInterface == "llamacpp":
            default = config.llamacppMainModel_max_tokens
        elif config.llmInterface == "ollama":
            default = config.ollamaMainModel_num_predict
        elif config.llmInterface == "groq":
            default = config.groqApi_max_tokens
        maxtokens = SinglePrompt.run(style=self.promptStyle, validator=NumberValidator(), default=str(default))
        if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
            maxtokens = int(maxtokens)
            if config.llmInterface == "gemini":
                config.geminipro_max_output_tokens = maxtokens
            elif config.llmInterface == "llamacpp":
                config.llamacppMainModel_max_tokens = maxtokens
            elif config.llmInterface == "ollama":
                config.ollamaMainModel_num_predict = maxtokens
            elif config.llmInterface == "groq":
                config.groqApi_max_tokens = maxtokens
            saveConfig()
            print3(f"Maximum output tokens: {maxtokens}")

    def setSystemMessage(self):
        # completer
        #Plugins.runPlugins()
        #completer = FuzzyCompleter(WordCompleter(list(config.predefinedContexts.values()), ignore_case=True))
        # history
        historyFolder = os.path.join(config.localStorage, "gchat")
        system_message_history = os.path.join(historyFolder, "system_message")
        system_message_session = PromptSession(history=FileHistory(system_message_history))
        # prompt
        print2("Change system message below:")
        prompt = SinglePrompt.run(style=self.promptStyle, promptSession=system_message_session, default=config.systemMessage_groq)
        if prompt and not prompt == config.exit_entry:
            config.systemMessage_groq = prompt
            saveConfig()
            print2("System message changed!")
            clear()
            self.messages = self.resetMessages()
            print("New chat started!")

    def run(self, prompt=""):
        if self.defaultPrompt:
            prompt, self.defaultPrompt = self.defaultPrompt, ""
        historyFolder = os.path.join(config.localStorage, "gchat")
        chat_history = os.path.join(historyFolder, "groq")
        chat_session = PromptSession(history=FileHistory(chat_history))

        print2(f"\n{self.name} loaded!")
        print2("```system message")
        print1(config.systemMessage_groq)
        print2("```")
        #if hasattr(config, "currentMessages"):
        #    bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        #else:
        #    bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
        #    print("(To start a new chart, enter '.new')")
        bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        print(f"(To exit, enter '{config.exit_entry}')\n")
        while True:
            completer = None if hasattr(config, "currentMessages") else FuzzyCompleter(WordCompleter([".new", ".api", ".model", ".systemmessage", ".temperature", ".maxtokens", ".togglewordwrap", ".togglevoiceoutput", config.exit_entry], ignore_case=True))
            if not prompt:
                prompt = SinglePrompt.run(style=self.promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, completer=completer)
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append(userMessage)
            else:
                prompt = SinglePrompt.run(style=self.promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True, completer=completer)
                userMessage = {"role": "user", "content": prompt}
                self.messages.append(userMessage)
            if prompt == config.exit_entry:
                break
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".togglevoiceoutput":
                config.ttsOutput = not config.ttsOutput
                saveConfig()
                print3(f"TTS Output: {config.ttsOutput}")
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".togglewordwrap":
                config.wrapWords = not config.wrapWords
                saveConfig()
                print3(f"Word Wrap: {config.wrapWords}")
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".temperature":
                self.setTemperature()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".maxtokens":
                self.setMaxTokens()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".systemmessage":
                self.setSystemMessage()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".api":
                self.changeGroqApi()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".model":
                self.setLlmModel_groq()
            elif not hasattr(config, "currentMessages") and prompt.lower() == ".new":
                clear()
                self.messages = self.resetMessages()
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                config.pagerContent = ""

                try:
                    completion = getGroqClient().chat.completions.create(
                        model=config.groqApi_chat_model,
                        messages=self.messages,
                        temperature=self.temperature,
                        max_tokens=config.groqApi_max_tokens,
                        n=1,
                        stream=True,
                        **config.groqApi_chat_model_additional_chat_options,
                    )

                    # Create a new thread for the streaming task
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    streamingWordWrapper.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    # add response to message chain
                    self.messages.append({"role": "assistant", "content": config.new_chat_response})
                except:
                    #self.streaming_thread.join()
                    print2(traceback.format_exc())

            prompt = ""

        print2(f"\n{self.name} closed!")
        if hasattr(config, "currentMessages"):
            print2(f"Return back to {config.freeGeniusAIName} prompt ...")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="gchat cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help=f"specify maximum output tokens with -o flag; default: {config.groqApi_max_tokens}")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help=f"specify temperature with -t flag: default: {config.llmTemperature}")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = config.groqApi_max_tokens
    else:
        max_output_tokens = config.groqApi_max_tokens
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = config.llmTemperature
    else:
        temperature = config.llmTemperature
    GroqChatbot(
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    ).run(
        prompt=prompt,
    )

if __name__ == '__main__':
    main()