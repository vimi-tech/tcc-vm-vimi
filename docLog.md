<h1> 
Programação de fluxo de login
<h2>  
<p>1- Instalação da Biblioteca oficial do Google para que o nosso código converse com o Firebase.</p>
<img width="790" height="333" alt="Captura de tela 1" src="https://github.com/user-attachments/assets/5107dde2-ccc6-47bb-8e68-b4503bac46e0" />
  <h2>Que já está instalada no nosso projeto:</h2>
  <img width="495" height="217" alt="Captura de tela 2026-04-17 210707" src="https://github.com/user-attachments/assets/19f8f886-512b-4df4-8c03-c92ee98ac86e" />

<h2>
  
  <p>2-Para a inicialização do nosso projeto, se quisermos ter uma simplicidade na configuração do ambiente, podemos utilizar o Application Default Credentials, um sistema que ao invés de criarmos um arquivo .json com senhas e carregarmos todo o servidor, ele já identifica nosso projeto automaticamente.</p>
  <p>Agora se na inicialização, quisermos especificar os detalhes do nosso projeto usaremos a variável FIREBASE_CONFIG.</p>
  <img width="815" height="146" alt="Captura de tela 2026-04-17 205436" src="https://github.com/user-attachments/assets/ab3b77e0-9a4c-4c5c-b758-41db781d52de" />
   Damos: default_app = firebase_admin.initialize_app(), para que o SDK entre em ação, permitindo que o nosso projeto interaja com os recursos do Firebase.
</h2>
<h2>3- Utilização do Token de Atualização do OAuth 2.0</h2>
