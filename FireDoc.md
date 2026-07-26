<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Documentação</title>
</head>
<body>

  <h1>Documentação de Configuração do Ambiente e Serviços (Firebase & Cloud Shell)</h1>

  <h2>1. Seleção do Projeto e Acesso ao Console no Firebase</h2>
  <p>1. O usuário acessa o Console do Firebase.</p>
<img width="267" height="202" alt="Captura de tela 2026-07-26 111843" src="https://github.com/user-attachments/assets/733111a5-10ec-4c3b-8419-790d3ea4bc28" />


  <p>2. Na lista de projetos, seleciona-se o projeto do trabalho/sistema (ex.: tarefaicoma).</p>
<img width="851" height="552" alt="Captura de tela 2026-07-26 111925" src="https://github.com/user-attachments/assets/d869745a-40e2-4576-8122-3f2df88a62c2" />

  <hr>

  <h2>2. Abertura do Cloud Shell no Google Cloud / Firebase</h2>
  <p>1. No painel do console, localiza-se e clica-se no ícone do Cloud Shell (&gt;_) localizado na barra superior/lateral direita.</p>
  <img width="317" height="226" alt="Captura de tela 2026-07-26 111937" src="https://github.com/user-attachments/assets/2e496d2a-919b-43a5-a0e8-c23329271e31" />

  <p>2. O terminal do Cloud Shell é inicializado na parte inferior da página, com a sessão configurada e apontada para o ID do projeto selecionado (ex.: tarefaicoma).</p>
  

  <hr>

  <h2>3. Configuração do Ambiente Virtual em Python (no Cloud Shell)</h2>
  <p>Para isolar as dependências da aplicação antes do deploy/automação, cria-se e ativa-se um ambiente virtual (venv):</p>

  <p>1. <strong>Criação do ambiente virtual:</strong></p>
  <code>python3 -m venv feirascore</code>
  <img width="1007" height="238" alt="Captura de tela 2026-07-26 112109" src="https://github.com/user-attachments/assets/cd076751-8593-4c12-a09d-5b019ef826ce" />


  <p>2. <strong>Verificação dos diretórios existentes:</strong></p>
  <code>ls</code>
  <img width="1013" height="220" alt="Captura de tela 2026-07-26 112124" src="https://github.com/user-attachments/assets/476c70ac-c997-4b4b-8c7b-9ae00979b180" />

  <p><em>Visualiza-se a pasta feirascore criada junto aos outros arquivos do projeto.</em></p>
  

  <p>3. <strong>Ativação do ambiente virtual:</strong></p>
  <code>source feirascore/bin/activate</code>
  <img width="1042" height="250" alt="Captura de tela 2026-07-26 112220" src="https://github.com/user-attachments/assets/7d723ce3-75f6-488d-b0e5-87bbf0af986a" />

  <p><em>Após a execução, o terminal exibe o prefixo (feirascore), indicando que o ambiente virtual está ativo.</em></p>

  <hr>

  <h2>4. Edição de Arquivos e Código (Cloud Shell Editor)</h2>
  <p>1. Para visualizar a estrutura de arquivos e editar o código ou documentos (como o README.md ou scripts de CI/CD), clica-se no botão "Abrir editor" (Cloud Shell Editor).</p>
  <img width="222" height="87" alt="Captura de tela 2026-07-26 112233" src="https://github.com/user-attachments/assets/b9756c53-2b73-4a39-be46-f9e01a1024fd" />

  <p>2. Na árvore de arquivos do editor, navega-se entre as pastas do projeto (como feirascore, tcc-vm-vimi, etc.) e cria-se ou edita-se os arquivos necessários para o fluxo de CI/CD do GitHub Actions e arquivos de configuração do Firebase.</p>
  <img width="371" height="151" alt="Captura de tela 2026-07-26 112313" src="https://github.com/user-attachments/assets/b2e52265-9b68-40ab-a7e7-994db12d00a3" />


  <hr>
<h2>5. Execução do Servidor de Desenvolvimento</h2>
<p>Execução no Terminal do VS Code:</p>
<p>1. O comando source devserver.sh é inserido no terminal integrado do editor para iniciar a rotina local de desenvolvimento.
<img width="886" height="211" alt="Captura de tela 2026-07-26 114907" src="https://github.com/user-attachments/assets/1a2ff097-99ff-4c12-b24c-697c78566ce8" /></p>

2.Carregamento no Shell Atual:
O utilitário source lê o arquivo e aplica as instruções e variáveis diretamente no processo do terminal em execução.

3.Subida do Servidor Local:
O script ativa o ambiente local de testes, liberando o servidor para validação do código e das integrações antes do deploy.</p>
  
</body>
</html>
