<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Passo a Passo da Implantação</title>
</head>
<body>

  <h1>Nosso Passo a Passo de Implantação</h1>

  <hr>

  <section>
        <h2> Nosso Servidor Local (Flask / Google Cloud Shell)</h2>
        <p>Nesta primeira etapa, nós estávamos executando a nossa aplicação localmente para testar se tudo funcionava perfeitamente antes de subirmos para a nuvem[cite: 3, 5].</p>
        <ul>
            <li><strong>O que nós fizemos:</strong> Nós acessamos o terminal do <strong>Google Cloud Shell</strong> no diretório <code>~/tco-vm-vimi</code> e iniciamos o projeto executando o comando <code>python3 main.py</code>[cite: 3, 7].</li>
            <li><strong>Status da nossa aplicação:</strong> O nosso servidor web em <strong>Flask</strong> começou a rodar no endereço local <code>http://127.0.0.1:5000</code>[cite: 3, 6].</li>
            <li><strong>Alertas no nosso terminal:</strong> O terminal nos avisou que o modo de depuração estava ligado (<em>Debug mode: on</em>) e nos lembrou que esse era apenas um servidor de desenvolvimento[cite: 4, 5]. Logo abaixo, vimos a opção de migração para o <strong>Render</strong>[cite: 8, 12].</li>
        </ul>
    </section>

   <hr>

  <section>
        <h2>  Criando o Nosso Espaço de Trabalho (Workspace no Render)</h2>
        <p>Na segunda tela, nós entramos no painel do <strong>Render</strong> para configurar o ambiente onde o nosso projeto iria ficar hospedado[cite: 8, 20].</p>
        <ul>
            <li><strong>O que nós fizemos:</strong> No menu da plataforma, nós acessamos a opção de alternar área de trabalho (<em>SWITCH WORKSPACE</em>) e clicamos no botão <strong>+ New Workspace</strong>[cite: 20, 26].</li>
            <li><strong>Preenchimento dos nossos dados:</strong> Acessamos a tela <strong>Create a New Workspace</strong> para preencher as informações[cite: 31, 32]:
                <ul>
                    <li><strong>Name:</strong> O nome que nós iríamos dar para a nossa área de trabalho[cite: 33].</li>
                    <li><strong>Billing Email:</strong> O nosso e-mail de cobrança cadastrado (<code>flopflopado96225@gmail.com</code>)[cite: 34, 35].</li>
                </ul>
            </li>
        </ul>
    </section>

   <hr>

  <section>
        <h2> Escolhendo o Nosso Plano de Hospedagem (Hobby)</h2>
        <p>Nesta terceira imagem, nós selecionamos o plano gratuito oferecido pelo Render para manter o nosso projeto no ar[cite: 37, 39, 41].</p>
        <ul>
            <li><strong>O plano que escolhemos:</strong> Nós selecionamos o plano <strong>Hobby</strong>, voltado para projetos pessoais e aplicações menores[cite: 37, 38, 41].</li>
            <li><strong>Custo:</strong> Nós não pagaríamos nada por mês (<strong>$0/mo</strong>) (<em>com possíveis custos adicionais de computação se excedêssemos os limites</em>)[cite: 39, 40].</li>
            <li><strong>O que nós ganhamos nesse plano:</strong>
                <ul>
                    <li>Um espaço de trabalho exclusivo para nós[cite: 43].</li>
                    <li>5 GB de limite de transferência de dados (<em>bandwidth</em>)[cite: 44].</li>
                    <li>Direito a 2 domínios personalizados[cite: 45].</li>
                    <li>500 minutos por mês para compilar o nosso código (<em>build minutes</em>)[cite: 46].</li>
                    <li>Projetos ilimitados com até 2 ambientes[cite: 47].</li>
                    <li>Permissão para subir até 25 serviços[cite: 48].</li>
                </ul>
            </li>
        </ul>
    </section>

   <hr>

   <section>
       <h2>  Conectando o Nosso GitHub ao Render</h2>
        <p>Na última tela, nós fizemos a conexão direta entre o código que estava no nosso repositório do <strong>GitHub</strong> e a plataforma do <strong>Render</strong> para publicar a aplicação[cite: 63, 78, 81].</p>
        <ul>
            <li><strong>No nosso GitHub (janela em destaque):</strong> Nós abrimos o nosso repositório <code>https://github.com/vimi-tech/tcc-vm-vimi.git</code> e copiamos o link no formato HTTPS[cite: 60, 63].</li>
            <li><strong>No Render (ao fundo):</strong> Na opção de criar um serviço usando um repositório público (<em>Public Git Repository</em>), nós colamos o link do nosso projeto e clicamos no botão <strong>Connect</strong> para integrar tudo e iniciar o deploy[cite: 78, 80, 81].</li>
        </ul>
    </section>

</body>
</html>
