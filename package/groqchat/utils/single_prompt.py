import textwrap
from groqchat import config
from groqchat import print2, print3, saveConfig, voiceTyping

from prompt_toolkit import prompt
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal


class SinglePrompt:

    @staticmethod
    def run(inputIndicator="", validator=None, default="", accept_default=False, completer=None, promptSession=None, style=None, is_password=False, bottom_toolbar=None, **kwargs):
        this_key_bindings = KeyBindings()
        @this_key_bindings.add(*config.hotkey_exit)
        def _(event):
            buffer = event.app.current_buffer
            buffer.text = config.exit_entry
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_cancel)
        def _(event):
            buffer = event.app.current_buffer
            buffer.reset()
        @this_key_bindings.add(*config.hotkey_insert_newline)
        def _(event):
            buffer = event.app.current_buffer
            buffer.newline()
        @this_key_bindings.add(*config.hotkey_toggle_word_wrap)
        def _(_):
            config.wrapWords = not config.wrapWords
            saveConfig()
            run_in_terminal(lambda: print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_response_audio)
        def _(_):
            if config.tts:
                config.ttsOutput = not config.ttsOutput
                saveConfig()
                run_in_terminal(lambda: print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_new)
        def _(event):
            buffer = event.app.current_buffer
            config.defaultEntry = buffer.text
            buffer.text = ".new"
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_voice_entry)
        def _(event):
            if config.pyaudioInstalled:
                buffer = event.app.current_buffer
                buffer.text = f"{buffer.text}{' ' if buffer.text else ''}{voiceTyping()}"
                if config.voiceTypingAutoComplete:
                    buffer.validate_and_handle()
                else:
                    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
            else:
                run_in_terminal(lambda: print2("Install PyAudio first to enable voice entry!"))

        config.selectAll = False
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = [
                ("class:indicator", ">>> "),
            ]
        userInput = inputPrompt(
            inputIndicator,
            key_bindings=this_key_bindings,
            bottom_toolbar=bottom_toolbar if bottom_toolbar is not None else f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}""",
            #enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=style,
            validator=validator,
            multiline=Condition(lambda: hasattr(config, "currentMessages") and config.multilineInput),
            default=default,
            accept_default=accept_default,
            completer=completer,
            is_password=is_password,
            mouse_support=False,
            **kwargs,
        )
        userInput = textwrap.dedent(userInput) # dedent to work with code block
        return userInput if hasattr(config, "addPathAt") and config.addPathAt else userInput.strip()
