 <h1>Guia Passo a Passo: Criação de Workspace e Conexão de Repositório no Render</h1>


 <h1>Passo 1: Acessar a Plataforma e Iniciar o Cadastro</h1>
    <p>Acesse o site oficial do Render. Na página inicial, clique no botão "Start for free" (ou no botão "Migrate to Render", caso esteja vindo de outro provedor).
    <img width="1115" height="728" alt="Captura de tela 2026-07-31 174518" src="https://github.com/user-attachments/assets/6bc7db0b-e69c-42a8-a475-14c4ba3f766f" />

</p>

  <p> Criar uma conta no Render é gratuito e não exige cartão de crédito imediatamente para projetos menores (plano Hobby).</p>

  <h1>Passo 2: Acessar ou Criar um Novo Workspace</h1>

  <p>Na Dashboard do Render, clique sobre o nome do seu Workspace atual no canto superior esquerdo para abrir o menu suspenso. Clique na opção "+ New Workspace" para criar um novo ambiente isolado para o seu projeto.
<img width="635" height="575" alt="Captura de tela 2026-08-11 144513" src="https://github.com/user-attachments/assets/4b4294bb-eb72-45b2-9469-cc0645b0fdff" />

</p>

 <p> Separar seus projetos em diferentes Workspaces é uma boa prática para organizar permissões, faturamento (billing) e serviços de forma independente.</p>

 <h1>Passo 3: Configurar os Detalhes do Workspace</h1>

 <p>No formulário Workspace Details: Insira o Name (Nome) do seu novo workspace e verifique o Billing Email (E-mail de Cobrança) associado.
 <img width="738" height="363" alt="Captura de tela 2026-08-11 144518" src="https://github.com/user-attachments/assets/4c9e6c19-b827-4431-b04e-719da01bfac0" />

 </p>

  <p> Escolha um nome claro que identifique o projeto ou cliente (ex: TCC-Vimi ou Projeto-Producao).</p>

 <h1>Passo 4: Seleção de Plano (Plano Hobby)</h1>

  <p>Confirme a seleção do plano Hobby (gratuito) clicando em Plan selected. O plano inclui: $0/mês (custos de computação grátis com limites), 5 GB de largura de banda (bandwidth), 2 domínios customizados, 500 minutos de build e deploy de até 25 serviços.
  <img width="495" height="598" alt="Captura de tela 2026-08-11 144534" src="https://github.com/user-attachments/assets/83daecb2-6437-4602-9361-b6f978199ee4" />

  </p>

  <p> O plano Hobby é ideal para testes, TCCs e aplicações de pequeno porte.</p>

 <h1>Passo 5: Obter a URL do Repositório no GitHub</h1>

 <p>Acesse o repositório do seu projeto no GitHub (no caso: vimi-tech/tcc-vm-vimi). Clique no botão verde "<> Code", certifique-se de selecionar a aba HTTPS e copie o endereço completo (ex: https://github.com/vimi-tech/tcc-vm-vimi.git).
 <img width="542" height="449" alt="Captura de tela 2026-08-11 144539" src="https://github.com/user-attachments/assets/eb1f4c50-2505-435a-ab5b-2addc60878fb" />

 </p>

 <p>Para utilizar a opção de Public Git Repository no Render, certifique-se de que o repositório no GitHub está configurado como Público.</p>

  <h1>Passo 6: Conectar o Repositório Público no Render</h1>

 <p>De volta ao Render, na tela de novo serviço/deploy, selecione a aba "Public Git Repository". Cole a URL copiada no campo de texto:

<img width="586" height="171" alt="Captura de tela 2026-08-11 144544" src="https://github.com/user-attachments/assets/e31412fb-3f01-4d5c-bec7-9a06fc675d49" />


