🛡️ OpenVAS Automation & n8n Integration Pipeline
Este documento serve como guia de implementação para o projeto de automação de Análise de Vulnerabilidades. O objetivo é provisionar o OpenVAS (Greenbone Vulnerability Management) via Docker, automatizar scans via CLI e integrar os resultados (relatórios JSON) com um fluxo de orquestração no n8n.

📋 Escopo do Projeto
O projeto consiste em criar um ambiente containerizado onde o OpenVAS realiza varreduras sob demanda e reporta os achados automaticamente para um webhook externo.

Objetivos Principais
Infraestrutura: Deploy do OpenVAS via Docker.

Operação: Configuração e execução de scans via linha de comando (CLI/API).

Integração: Exportação e envio do relatório (JSON) para n8n.

Qualidade: Camada de testes e documentação técnica completa.

🗺️ Roadmap de Desenvolvimento (Para Jules)
Fase 1: Infraestrutura (Docker)
[ ] Configurar Docker Compose:

Criar arquivo docker-compose.yml utilizando as imagens oficiais greenbone/community-containers.

Garantir persistência de dados (volumes para redis, db, gvmd).

Expor portas necessárias para acesso Web (GSA) e comunicação GMP (Greenbone Management Protocol).

[ ] Provisionar n8n (Opcional/Local):

Subir um container simples do n8n para receber os testes de webhook.

Fase 2: Configuração e Automação (CLI)
[ ] Configuração via CLI:

Utilizar gvm-tools (gvm-cli) para interagir com o socket do OpenVAS.

Script para criar/atualizar um Target (IP alvo).

Script para criar uma Task de scan associada ao target.

[ ] Execução do Scan:

Comando para iniciar o scan via terminal.

Nota: Para testes, utilizar um IP controlado (ex: scanme.nmap.org ou container local vulnerável como dvwa) para evitar problemas éticos/legais com "IPs aleatórios".

Fase 3: Integração e Extração de Dados
[ ] Análise de Integração Nativa:

Investigação: Verificar se a funcionalidade de "Alerts" do OpenVAS suporta envio de payload completo do relatório via HTTP POST para o webhook.

[ ] Desenvolvimento de Script Python (Caso a nativa seja insuficiente):

Utilizar biblioteca python-gvm.

Lógica:

Monitorar o status do scan até Done.

Recuperar o ID do relatório gerado.

Baixar o relatório no formato JSON.

Enviar payload via requests.post para o Webhook do n8n.

Fase 4: Camada de Testes (QA)
[ ] Teste de Implementação OpenVAS: Verificar se os serviços subiram e se a interface web está acessível.

[ ] Teste de Implementação n8n: Verificar recebimento de requests no Webhook.

[ ] Teste de Integração: Rodar o script Python e validar se o JSON chegou no n8n corretamente estruturado.

[ ] Teste End-to-End: Rodar comando make scan-and-report (sugestão) e verificar o fluxo completo sem intervenção manual.

🛠️ Requisitos Técnicos
Stack Tecnológica
Engine: Greenbone Community Edition (Docker).

Orquestração: Docker Compose.

Linguagem de Automação: Python 3.9+ (libs: python-gvm, requests).

Destino: n8n Webhook.

Estrutura de Diretórios Sugerida
Bash

.
├── docker-compose.yml       # Orquestração do OpenVAS
├── scripts/
│   ├── setup_openvas.sh     # Configuração inicial (usuários, feeds)
│   ├── run_scan.py          # Script principal de automação
│   └── requirements.txt     # Dependências Python
├── docs/
│   ├── installation.md
│   └── api_reference.md
└── README.md
📝 Requisitos de Documentação
A entrega final deve conter uma documentação detalhada cobrindo:

Como Subir: Passos exatos para rodar o docker-compose up e aguardar o sync dos feeds.

Como Configurar: Explicação dos parâmetros do script Python (ex: definir IP alvo, definir URL do n8n).

Guia de Integração:

Explicação da decisão tomada (Nativa vs Script Python).

Exemplo do JSON gerado.

Relatório de Testes:

Evidências (prints ou logs) de que o scan rodou.

Evidência do n8n recebendo os dados.

Pontos de Observação:

Tempo médio de scan.

Consumo de recursos (RAM/CPU) dos containers.

Dificuldades encontradas com a API GMP.

⚠️ Critérios de Aceite
O projeto só será considerado concluído se:

O OpenVAS estiver rodando em Docker estável.

Um comando único disparar o processo de Scan -> Extração -> Envio.

O n8n receber o JSON contendo as vulnerabilidades detectadas.

O código estiver comentado e a documentação clara para reprodução em outro ambiente.
