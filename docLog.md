<h1> Programação de fluxo de login

<h2> 1- Configurar um projeto e uma conta de serviço do Firebase.</h2>
  
<p> Precisaremos de:
  
  •Um projeto do Firebase (Já temos).
  <img width="258" height="97" alt="Captura de tela 2026-04-17 235846" src="https://github.com/user-attachments/assets/e21fa294-d3c1-48ea-bc11-d29d38d2bb44" />

  •Uma conta de serviço do SDK Admin do Firebase para se comunicar com o Firebase (Já foi gerada com a criação do nosso projeto).

  •Um arquivo de configuração com as credenciais da sua conta de serviço (Já criamos e está armazenada no Gmail).
  </p>
  <p>Instalação da Biblioteca oficial do Google para que o nosso código converse com o Firebase:</p>
<img width="993" height="302" alt="Captura de tela 2026-04-18 001052" src="https://github.com/user-attachments/assets/80b3b570-3ceb-49a1-aa30-0c8ccf843415" />

  <P>Que já está instalada no nosso projeto:</P>
  <img width="495" height="217" alt="Captura de tela 2026-04-17 210707" src="https://github.com/user-attachments/assets/19f8f886-512b-4df4-8c03-c92ee98ac86e" />


  
  <p>2-Para a inicialização do nosso projeto, se quisermos ter uma simplicidade na configuração do ambiente, podemos utilizar o Application Default Credentials, um sistema que ao invés de criarmos um arquivo .json com senhas e carregarmos todo o servidor, ele já identifica nosso projeto automaticamente.</p>
  <p>Agora se na inicialização, quisermos especificar os detalhes do nosso projeto usaremos a variável FIREBASE_CONFIG.</p>
  <img width="815" height="146" alt="Captura de tela 2026-04-17 205436" src="https://github.com/user-attachments/assets/ab3b77e0-9a4c-4c5c-b758-41db781d52de" />
   Damos: default_app = firebase_admin.initialize_app(), para que o SDK entre em ação, permitindo que o nosso projeto interaja com os recursos do Firebase.
</h2>
<h2>3- Utilização do Token de Atualização do OAuth 2.0</h2>
 <P> Para obtermos uma autenticação segura, o SDK fornece um Token de Atualização.
 </P>
 <p>Mas o que é esse token?

  Um token de atualização foca na segurança, automatização e autenticação de aplicações de backend.
  Existindo dois tipos de credenciais que fazem parte da utilização do token:
  
  Access Token: Uma credencial que tem curta duração que autoriza solicitações dos recursos do Firebase que utilizaremos.
  
  Refresh Token: Uma credencial de longa duração, utilizada para obtermos exclusivamente novos Access Tokens quando eles expirarem, sem a necessidade de autorizações de solicitações para o uso dos recursos.
  
  E o SDK, basicamente monitora a validade dos tokens, então quando o Access Token expira ele verifica e pede para o  Refresh Token solicitar uma nova credencial.
 </p>
 <img width="1002" height="162" alt="Captura de tela 2026-04-17 225524" src="https://github.com/user-attachments/assets/c060aad3-1af3-4082-8091-debc323e6456" />

 <h2>Inicializar o SDK em ambientes que não são do Google.</h2>
<p>Quando nosso projeto está em um lugar que não é do ambiente Google,  torna-se necessário gerarmos uma Chave Privada no console do Firebase, para a autorização do uso do nosso banco de dados fora do Google ser permitida pelo própio, em outros ambientes fora dele.
Nessa chave contém códigos criptografados que precisam ser guardados com segurança, para que ninguém tenha acesso aos nossos dados.
Guardamos no Gmail:</p>
<img width="656" height="456" alt="Captura de tela Chave" src="https://github.com/user-attachments/assets/cd5f5489-1bbe-4464-b9df-7401b07c9230" />
Para utilizarmos a Chave em outro ambiente usamos a variável:
<img width="988" height="199" alt="Captura de tela 2026-04-17 232919" src="https://github.com/user-attachments/assets/cab30658-9c40-4a78-adba-6594ac4903a3" />
Inicializamos o SDK:
<img width="999" height="145" alt="Captura de tela 2026-04-17 232934" src="https://github.com/user-attachments/assets/e2507e40-a20d-4b3b-80d6-053808273886" />


<h2>Inicializar vários aplicativos</h2>
<p> Quando queremos gerenciar múltiplos projetos do Firebase, por exemplo: 

  Estamos lendo dados de um projeto e preciso escrever em outro.
  Então usamos os seguintes comandos:
  <img width="995" height="286" alt="Captura de tela 2026-04-18 001014" src="https://github.com/user-attachments/assets/541ecaf2-befc-4fcb-974a-af60a1ea1fe6" />

</p>
 
