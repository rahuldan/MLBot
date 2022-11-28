# MLBot

This is a project to track, stop and restart your ML training using a Slack App.

During training of ML models, you have to monitor the evaluation and training loss stats at a regular interval to ensure that the process is going smoothly and change the hyperparameters based on that, if needed. This tool helps to monitor the training/eval stats directly through your Slack, it even helps in stopping the training process and running it again with updated parameters remotely, when you don't have access to your workstation.

# How it works?

You start a local server that monitors your training logs, and install a Slack bot for your account. The local server establishes a socket connection with your Slack account, and takes actions whenever you send a query/stop/start message through your Slack.

# Video Tutorial

Link to the documentation guide: https://drive.google.com/file/d/1R_-JnSs7CmbJresASp6hIkn2iazCPPug/view?usp=sharing

You can either use the built main and init files from the GDrive or use the ones in the repo (init.py is in utils folder)

Follow through this tutorial video for the quick setup process:

[![](https://img.youtube.com/vi/n47kRdtixg0/0.jpg)](https://www.youtube.com/watch?v=n47kRdtixg0)
