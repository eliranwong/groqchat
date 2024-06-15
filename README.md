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

# Get Started

Simply run 'gchat':

> gchat

Enter your Groq cloud a single API key or a list of multiple API keys:<br>
(Remarks: If a list of multiple API keys are entered, entered API keys are automatically rotated for running inference.)

<img width="1004" alt="groqapi" src="https://github.com/eliranwong/groqchat/assets/25262722/a510f465-1768-4fcb-8ae5-cfab9f3adad8">

Select a model:

<img width="1004" alt="models" src="https://github.com/eliranwong/groqchat/assets/25262722/42cbcd85-b13a-4188-98e6-2abf99542993">

# Special Entry

Enter a dot '.' to display available special entry:

<img width="1004" alt="ui" src="https://github.com/eliranwong/groqchat/assets/25262722/31fa20e7-24cb-4aa1-b67e-38f6bf24971d">

'.new' - start a new chart session

'.api' - change api key

'.model' - change model

'.systemmessage' - change system message

'.temperature' - change temperature

'.maxtokens' - change max tokens

'.exit' - exit the application

# CLI Options

Run 'gchat --help' for cli options

> gchat --help

<img width="1004" alt="cli_option" src="https://github.com/eliranwong/groqchat/assets/25262722/eb58aeaf-7cc7-4170-b253-1200b99d57e9">

For example, to start with a greeting:

> gchat "Hi!"

For example, to set temperature to 0.8 and maximum output tokens to 1024, run:

> gchat -t 0.8 -o 1024 "Hi!"
