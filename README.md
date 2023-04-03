# Protipo Carrinho

Este repositório inclui três Scripts.

ScriptServidor: Serve como script que corre numa raspberry, recebe dados vindos de um script numa máquina cliente e ativa uma LED de acordo com os dados lidos .

ScriptCliente: Lê um código de barras, input vindo de um leitor de código de barras, e envia esse código para um script a correr na mesma máquina.

ScriptEmuMTS: Simula uma base de dados do MTS com um dicionário, serve para receber o código de barras lido e enviar para a raspberry o código de LED a ligar.

Comunicação entre ScriptServidor e ScriptEmuMTS é feita atrvez de HTTP POST
