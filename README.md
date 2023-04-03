# Protipo Carrinho

Este repositório inclui três Scripts.

ScriptServidor: Serve como script que corre numa raspberry, recebe dados vindos de um script numa máquina cliente e ativa uma LED de acordo com os dados lidos .

ScriptCliente: Lê um código de barras, input vindo de um leitor de código de barras, e envia esse código para um script a correr na mesma máquina.

ScriptEmuMTS: Simula uma base de dados do MTS com um dicionário, serve para receber o código de barras lido e enviar para a raspberry o código de LED a ligar.

Comunicação entre ScriptServidor e ScriptEmuMTS é feita atrvez de HTTP POST

# Prototype Cart

This repository includes three Scripts.

ScriptServer: Serves as a script that runs on a raspberry, receives data coming from a script on a client machine and activates a LED according to the read data.

ScriptClient: Reads a barcode, input coming from a barcode reader, and sends that code to a script running on the same machine.

ScriptEmuMTS: Simulates a MTS database with a dictionary, it receives the barcode read and sends to the raspberry the LED code to be connected.

Communication between ScriptServer and ScriptEmuMTS is done through HTTP POST

Translated with www.DeepL.com/Translator (free version)
