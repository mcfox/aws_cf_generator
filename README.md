# Instalação de Produção ou Homologação

Para instalar o aplicativo, temos 2 arquivos do Cloud Formation:

- O primeiro para montar a maquina base onde os aplicativos irão rodar, que a partir desse EC2
iremos gerar a AMI base para as maquinas de homologação e produção

- O segundo é para montar o STACK completo do aplicativo, que usa como
parametro o ID da AMI gerada pelo primeiro CF


- Entre no Cloud Formation: https://console.aws.amazon.com/cloudformation
- Clique em Create Stack e informe o CF da AMI e execute
- Como output teremos o id da maquinda criada
- Entre no EC2 e a partir dessa maquina crie uma AMI.
- Anote o AMI dessa AMI e altere o default do CF do Stack para esse novo ID


   Durante a criacao da maquina, o log é criado esta no /tmp/user_data.log
   
    tail -f /tmp/user_data.log



- Entre no Cloud Formation novamente
- Clique em Create Stack e informe o agora o segundo CF do Stack e execute
- Como output teremos o DNS de entrada no stack completo do aplicativo
- Entre no Aplicativo e faça um ciclo completo de uso para validar a instalação




# Cloud Formation (CF)

Para criar os arquivos do CF usamos as seguintes ferramentas:

### Throposhpere
https://github.com/cloudtools/troposphere

### CF Designer:
https://console.aws.amazon.com/cloudformation/designer/home?region=us-east-1

Primeiro instale o troposphere na sua maquina

    https://github.com/cloudtools/troposphere
    $ pip install troposphere


Para gerar o cloud formation, execute o arquivo aws_stack.py com o python

    python aws_stack.py
    
Responda as perguntas e no final um novo arquivo .json será criado

Voce pode abrir o Json gerado para visualizar a arquiterura do aplicativo:

![stack](app-cf-designer.png)

