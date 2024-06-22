# groqchat

A terminal chatbot, powered by Groq Cloud API (Windows / macOS / Linux / Android / iOS)

Modified groq chatbot developed in https://github.com/eliranwong/freegenius

A simple chatbot that runs fast on mobile phones as well as pc.

# Groq API Key

Get a Groq API key first. Read https://github.com/eliranwong/freegenius/wiki/Set-up-a-Groq-Cloud-API-Key

# Android / iOS / iPhone / iPad Users

iOS/iPad/iPhone: Use [iSH](https://ish.app/) on iOS/iPad/iPhone.

Android: Use [Termux](https://termux.dev/en/) on Android.

# Installation

With python installed, setup gropchat via pip:

> pip install groqchat

Or

> pip install gchat

# Android Users

1. Install rust

> pkg install rust

2. Use "--system-site-packages" if you create a virtual environment, e.g.

> python -m venv gchat --system-site-packages

> source gchat/bin/activate

> pip install --upgrade gchat

On Android, use Android built-in voice typing keyboards of Ctrl+S.

Install [Termux:API](https://wiki.termux.com/wiki/Termux:API), to work with response output on Andoird.

# Get Started

Simply run 'gchat':

> gchat

Enter your Groq cloud a single API key or a list of multiple API keys:<br>
(Remarks: If a list of multiple API keys are entered, entered API keys are automatically rotated for running inference.)

<img width="1004" alt="groqapi" src="https://github.com/eliranwong/groqchat/assets/25262722/a510f465-1768-4fcb-8ae5-cfab9f3adad8">

Select a model:

<img width="1004" alt="models" src="https://github.com/eliranwong/groqchat/assets/25262722/42cbcd85-b13a-4188-98e6-2abf99542993">

# Special Entries

Enter a dot '.' to display available special entries:

<img width="1004" alt="ui" src="https://github.com/eliranwong/groqchat/assets/25262722/31fa20e7-24cb-4aa1-b67e-38f6bf24971d">

'.new' - start a new chart session

'.api' - change api key

'.model' - change model

'.systemmessage' - change system message

'.temperature' - change temperature

'.maxtokens' - change max tokens

'.togglewordwrap' - toggle word wrap

'.togglevoiceoutput' - toggle voice output

'.exit' - exit the application

# Keyboard Shortcuts

By default:

Ctrl+Z - cancel

Ctrl+Q - exit / quit

Ctrl+I / TAB - insert new line

Ctrl+N - new chat session

Ctrl+W - toggle word wrap

Ctrl+Y - toggle voice output

Ctrl+S - trigger voice typing

# Configurations

Advanced users may change configurations manually by editing the file "config.py" located in the package folder.

Remarks: Close the app before editing the file.

# CLI Options

Run 'gchat --help' for cli options

> gchat --help

<img width="1004" alt="cli_option" src="https://github.com/eliranwong/groqchat/assets/25262722/eb58aeaf-7cc7-4170-b253-1200b99d57e9">

For example, to start with a greeting:

> gchat "Hi!"

For example, to set temperature to 0.8 and maximum output tokens to 1024, run:

> gchat -t 0.8 -o 1024 "Hi!"

# Install Multiple Copies

You may want to install multiple copies to customise them with different system messages or other settings.  

An easy way to achieve it is to use alias, e.g.:

> mkdir apps

> cd apps

> python3 -m venv assist explain quote illustrate summarize

> source assist/bin/activate

> pip install gchat

> source explain/bin/activate

> pip install gchat

> source quote/bin/activate

> pip install gchat

> source illustrate/bin/activate

> pip install gchat

> source summarize/bin/activate

> pip install gchat

> nano .bashrc

Add the following aliases:

```
alias explain=$HOME/apps/explain/bin/gchat
alias illustrate=$HOME/apps/illustrate/bin/gchat
alias quote=$HOME/apps/quote/bin/gchat
alias assist=$HOME/apps/assist/bin/gchat
alias summarize=$HOME/apps/summarize/bin/gchat
```
