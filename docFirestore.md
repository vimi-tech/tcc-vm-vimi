# Cloud Firestore 
O Cloud Firestore é um banco de dados NoSQL escalonável e flexível do Google Cloud, focado no armazenamento e sincronização de dados entre servidores e clientes. Ele se destaca pela capacidade de manter dados em sincronia em tempo real e por oferecer suporte off-line, o que permite que os aplicativos funcionem perfeitamente mesmo sem conexão estável com a internet.
<img width="857" height="261" alt="Firebaseadmin" src="https://github.com/user-attachments/assets/051b87b8-9474-4c2b-b4ae-8bbd91730e4a" />
No contexto deste projeto, a utilização do serviço é viabilizada pela presença do Firebase Admin SDK, conforme demonstrado no arquivo de dependências. Essa configuração estabelece a base necessária para que o código Python interaja de forma administrativa e segura com o banco de dados, permitindo a gestão completa de documentos e coleções diretamente pelo backend da aplicação.

# 1- Principais Recursos 
## Flexibilidade:
O Cloud Firestore permite armazenar dados de forma flexível e organizada em documentos dentro de coleções. Esses documentos podem ter estruturas complexas, com objetos aninhados e até subcoleções.

## Consultas expressivas:
O Cloud Firestore permite fazer consultas com filtros e ordenação para buscar documentos específicos ou conjuntos de dados.

## Atualizações em tempo real:
O Firestore sincroniza dados em tempo real entre dispositivos e também permite consultas rápidas e eficientes.

## Suporte off-line:
O Cloud Firestore permite usar o app mesmo offline, armazenando dados em cache para leitura, escrita e consultas. Quando a conexão retorna, ele sincroniza automaticamente as alterações com o banco de dados.

## Projetado para escala:
O Cloud Firestore é projetado para escalar, usando a infraestrutura do Google Cloud com replicação automática, alta consistência, operações em lote e suporte a transações seguras (ACID), sendo capaz de lidar com grandes volumes de dados e aplicações complexas.

# 2- Como funciona?
<img width="443" height="247" alt="Captura de tela 2026-04-20 201221" src="https://github.com/user-attachments/assets/bcdfb7f6-3359-48fe-8d08-3d8038c9ad5a" />
Uma pasta usada para organizar arquivos: ela representa uma collection, onde os dados ficam agrupados. Dentro dessa pasta estão os “papéis”, que são os documents, e cada documento contém as informações (data). Assim, no Cloud Firestore, os dados são armazenados em documentos, que ficam dentro de coleções, criando uma estrutura organizada e fácil de entender.

# Modelo de dados do Cloud Firestore
## 1. Documentos:
No Cloud Firestore, o documento é a unidade básica de armazenamento, contendo campos com valores e identificado por um nome. 
<img width="668" height="160" alt="Captura de tela 2026-04-20 202251" src="https://github.com/user-attachments/assets/1cbeac98-10e9-422b-b86e-5388c818b22c" />
Esse exemplo mostra um documento no Firestore representando um usuário chamado “alovelace”. O nome “alovelace” é o identificador do documento. Dentro dele, existem campos com seus valores: “first” guarda o nome “Ada”, “last” guarda o sobrenome “Lovelace” e “born” guarda o ano de nascimento, 1815.

## 2. Coleções:
No Firestore, cada documento pode ter campos diferentes, mas é recomendado manter um padrão para facilitar as consultas. A coleção só guarda documentos (não guarda dados diretamente), e cada documento tem um nome único. Além disso, a coleção só existe quando há documentos dentro dela — se todos forem apagados, ela deixa de existir.
<img width="513" height="345" alt="Captura de tela 2026-04-20 202520" src="https://github.com/user-attachments/assets/dbcb47a8-9448-488e-9776-e39e67bfcc11" />
Na imagem, “usuários” é uma coleção, que funciona como uma pasta. Dentro dela existem vários documentos, como “alovelace” e “aturing”, e cada um representa um usuário com seus próprios dados.

## 3. Referências:
Uma referência é como um “endereço” do documento no banco de dados. Ela não traz os dados, apenas indica onde eles estão.
<img width="964" height="188" alt="Captura de tela 2026-04-20 203004" src="https://github.com/user-attachments/assets/a082cb16-8a6d-452e-97a2-7239443af49c" />
No exemplo, o código aponta para o documento “alovelace” dentro da coleção “users”.

## 4. Dados Hierárquicos:
A coleção “rooms” guarda as salas de conversa. Cada sala é um documento. Como uma sala pode ter muitas mensagens, em vez de colocar tudo dentro do documento, você cria uma subcoleção dentro dele, chamada por exemplo “messages”.
<img width="676" height="238" alt="Captura de tela 2026-04-20 203411" src="https://github.com/user-attachments/assets/4c3cf948-736d-4025-b885-1b7f06fe30ba" />
Assim, fica hierárquico: a coleção “rooms” contém os documentos (salas), e cada sala contém outra coleção com suas mensagens. Isso mantém os dados organizados e evita sobrecarregar um único documento.

## 4. Subcoleções:
<img width="848" height="496" alt="Captura de tela 2026-04-20 204404" src="https://github.com/user-attachments/assets/109d7f22-0ce7-41ed-9a61-2284d0a11588" />
Nesse caso, cada sala da coleção “rooms” pode ter uma subcoleção chamada “messages”, onde ficam armazenadas as mensagens daquela sala.

## Referência para uma mensagem na subcoleção
<img width="975" height="220" alt="Captura de tela 2026-04-20 204638" src="https://github.com/user-attachments/assets/71f1e4c8-893b-4a5f-960f-0aee7fb9fc57" />
No Cloud Firestore, os dados seguem sempre um padrão: coleção → documento → coleção → documento. Não é possível ter coleção dentro de coleção diretamente, nem documento dentro de documento sem esse intervalo.

