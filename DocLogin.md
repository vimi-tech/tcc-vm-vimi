<h1> Programação de fluxo de login

<h2> 1- Configurar um projeto e uma conta de serviço do Firebase.</h2>
  
<p> Precisaremos de:
  
  •Um projeto do Firebase (Já temos).
  
  •Uma conta de serviço do SDK Admin do Firebase para se comunicar com o Firebase (Já foi gerada com a criação do nosso projeto).
  
  •Um arquivo de configuração com as credenciais da sua conta de serviço (Já criamos e está armazenada no Gmail).
  </p>
 <h1>Instalação da Biblioteca oficial do Google para que o nosso código converse com o Firebase:</h1>
 
<img width="808" height="333" alt="Captura de tela 2026-04-17 185626" src="https://github.com/user-attachments/assets/0fe402ad-1313-4d5d-8893-35e0be23068e" />


<h1>Que já está instalada no nosso projeto:</h1>

  <img width="495" height="217" alt="Captura de tela 2026-04-17 210707" src="https://github.com/user-attachments/assets/19f8f886-512b-4df4-8c03-c92ee98ac86e" />


  <h2>2- Inicializar o SDK.</h2>
  <p>Para a inicialização do nosso projeto, se quisermos ter uma simplicidade na configuração do ambiente, podemos utilizar o Application Default Credentials, um sistema que ao invés de criarmos um arquivo .json com senhas e carregarmos todo o servidor, ele já identifica nosso projeto automaticamente.</p>
  <p>Agora se na inicialização, quisermos especificar os detalhes do nosso projeto usaremos a variável FIREBASE_CONFIG.</p>
  
  <img width="815" height="146" alt="Captura de tela 2026-04-17 205436" src="https://github.com/user-attachments/assets/ab3b77e0-9a4c-4c5c-b758-41db781d52de" />
  
   Damos: default_app = firebase_admin.initialize_app(), para que o SDK entre em ação, permitindo que o nosso projeto interaja com os recursos do Firebase.

<h2>3- Utilização do Token de Atualização do OAuth 2.0.</h2>
 <P> Para obtermos uma autenticação segura, o SDK fornece um Token de Atualização.
 </P>
 <p>Mas o que é esse token?

  Um token de atualização foca na segurança, automatização e autenticação de aplicações de backend.
  Existindo dois tipos de credenciais que fazem parte da utilização do token:</P>
  
  <h1>Access Token: Uma credencial que tem curta duração que autoriza solicitações dos recursos do Firebase que utilizaremos.</h1>
  
  
  <h1>Refresh Token: Uma credencial de longa duração, utilizada para obtermos exclusivamente novos Access Tokens quando eles expirarem, sem a necessidade de autorizações de solicitações para o uso dos recursos.</h1>
  
  <p>E o SDK, basicamente monitora a validade dos tokens, então quando o Access Token expira ele verifica e pede para o  Refresh Token solicitar uma nova credencial.
 </p>
 
 <img width="1002" height="162" alt="Captura de tela 2026-04-17 225524" src="https://github.com/user-attachments/assets/c060aad3-1af3-4082-8091-debc323e6456" />

 <h2>4- Inicializar o SDK em ambientes que não são do Google.</h2>
<p>Quando nosso projeto está em um lugar que não é do ambiente Google,  torna-se necessário gerarmos uma Chave Privada no console do Firebase, para a autorização do uso do nosso banco de dados fora do Google ser permitida pelo própio, em outros ambientes fora dele.
Nessa chave contém códigos criptografados que precisam ser guardados com segurança, para que ninguém tenha acesso aos nossos dados.
Guardamos no Gmail:</p>

<img width="656" height="456" alt="Captura de tela Chave" src="https://github.com/user-attachments/assets/cd5f5489-1bbe-4464-b9df-7401b07c9230" />

Para utilizarmos a Chave em outro ambiente usamos a variável:

<img width="988" height="199" alt="Captura de tela 2026-04-17 232919" src="https://github.com/user-attachments/assets/cab30658-9c40-4a78-adba-6594ac4903a3" />

Inicializamos o SDK:

<img width="999" height="145" alt="Captura de tela 2026-04-17 232934" src="https://github.com/user-attachments/assets/e2507e40-a20d-4b3b-80d6-053808273886" />


<h2>5- Inicializar vários aplicativos.</h2>
<p> Quando queremos gerenciar múltiplos projetos do Firebase, por exemplo: 

  Estamos lendo dados de um projeto e preciso escrever em outro.
  
  Então usamos os seguintes comandos:</p>
  
 <img width="1002" height="287" alt="Captura de tela 2026-04-18 001858" src="https://github.com/user-attachments/assets/a2de32f9-7c4b-4446-beca-a87e2d1e1a86" />
<h1>O comando App Default, gerencia UM ÚNICO PROJETO. 
  
Se precisamos acessar dois, três ou mais projetos, colocamos no INITIALIZE_APP para que mantenha as configurações de cada projeto separadas e organizadas.</h1>

<h2>6- Definir escopos para Realtime Database e Authentication.</h2>
<P>Se estamos utilizando uma VM(MMáquina Virtual) no Google Cloud (Compute Engine) com o Application Default Credentials do Google, teremos que configurar os escopos de acesso corretos.
  Então essa ação descreve as configurações necessárias para que a aplicação rode em instâncias do Google Compute Engine consigam interagir com APIs do Google Cloud/Firebase via Application Default Credentials.
  As APIs são interfaces de comunicação que permitem que o nosso código interaja com os serviços do Google.
  Então para atualizarmos as permissões de acesso (escopos) de uma máquina virtual já em uso no Google Cloud temos que:
</P>
<h2>Identificar:</h2>
<p>O sistema verifica a configuração atual para confirmar a conta de serviço vinculada à máquina.</p>
<H2>Desligar a Máquina:</H2>
<p>É obrigatório desligar a máquina virtual. As permissões de acesso não podem ser alteradas enquanto o sistema estiver em execução.</p>
<h2>Atualizar:</h2>
<p>A nova configuração de permissões à conta de serviço atualiza.</p>
<h2>Reinicializar:</h2>
<P>Ligar a máquina novamente para que as novas permissões entrem em ação.</P>

<img width="797" height="467" alt="Captura de tela 2026-04-18 125715" src="https://github.com/user-attachments/assets/16e5cd08-2c97-46dc-b3d7-dc1d20b9d908" />


<h2>7- Como testar com credenciais de usuário final da gcloud.</h2>
<P>Quando fizermos testes locais com o Firebase Authentication, o SDK utiliza requisitos de segurança mais rigorosos. 
A utilização do: gcloud auth application-default login gera credenciais de "usuário final" que o Firebase Auth não valida automaticamente por falta de um identificador de projeto claro e por não serem credenciais de serviço. Ou seja, O Firebase Authentication não aceita as credenciais padrão geradas pelo cliente OAuth da gcloud. Ele exige um contexto de projeto explícito e uma autenticação que ele reconheça como válida para operações administrativas ou de identificação de usuário.</P>

<h2>Para resolvermos o problema:</h2>
<h1>Utilizar nosso próprio ID de Cliente OAuth: </h1>
<p>Em vez de usar o ID padrão da gcloud, você deve gerar um ID de cliente no Console do Google Cloud e apontá-lo na autenticação.

Comando: gcloud auth application-default login --client-id-file=[/path/to/client/id/file]</P>
<img width="787" height="128" alt="Captura de tela 2026-04-18 132544" src="https://github.com/user-attachments/assets/8c23dd1e-69f7-472c-92d0-1e89eb787f91" />


<h1>Inserir o ID do projeto:
</h1>
<p>O SDK precisa saber exatamente em qual projeto atuar.</p>
<img width="819" height="237" alt="Captura de tela 2026-04-18 132550" src="https://github.com/user-attachments/assets/d77d1e2d-e45d-4370-8e14-7689feb4b437" />

 
