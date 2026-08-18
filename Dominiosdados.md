# Montagem de Dominios de Negócios para orientação dos projetos Finais [Dados].

## 1. Usuário
Armazena as informações das pessoas que navegam no sistema e efetuam o login para votar.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_usuario    | INT / UUID     | Primary Key    | Identificador único do usuário |
| email   | VARCHAR(255)   | Unique, Not Null    | E-mail para autenticação/login |
| codigo_confirmação  | VARCHAR(6)     | Not Null    | Código enviado por e-mail obrigatório para ativação do login |
| cpf  | VARCHAR(11)     | Unique, Not Null    | CPF do usuário para validação única |

## 2. Entrar como turma
Representa a turma responsável pelo projeto e estande, acessada via código de validação.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_turma   | UUID     | Primary Key, Auto Increment  | Identificador único da turma  |
| codigo_acesso | VARCHAR(10)   | Unique, Not Null    | Código inserido pela turma para liberar o cadastro do projeto |

## 3. Cadastro dos estandes
Armazena as informações do projeto submetido pela turma, que alimentará a página de Estandes.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_estande    | INT / UUID     | PK, Auto Increment  |Identificador único do estande/projeto |
| id_turma   | INT / UUID  | Unique, Not Null    | Vincula o estande à Turma responsável |
| nome_projeto | VARCHAR(100)     | Not Null    | Nome do projeto |
| descricao | TEXT    | Not Null   |Texto descritivo e explicativo do trabalho|
| url_foto | LONGBLOB   | Unique, Not Null    | Arquivo de imagem do estande (obrigatório) |
| url_video |  LONGBLOB  | Unique, Not Null    | Arquivo de vídeo do estande (obrigatório) |

## 4. Página de Estandes
Armazena os estandes cadastrados pelos alunos.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| nome_projeto | VARCHAR(100)     | Not Null    | Nome do projeto |
| descricao | TEXT    | Not Null   |Texto descritivo e explicativo do trabalho|
| url_foto | LONGBLOB   | Unique, Not Null    | Arquivo de imagem do estande (obrigatório) |
| url_video |  LONGBLOB  | Unique, Not Null    | Arquivo de vídeo do estande (obrigatório) |

## 5. Critérios para avaliação (votação) 
Armazena as perguntas para critérios de votação, que darão o pódio aos projetos.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_criterio | INT / UUID     |PK, Auto Increment   | Identificador único do critério de avaliação|
| id_estandes| INT / UUID  | Not Null   |Chave estrangeira que vincula o critério ao projeto (Estande) avaliado|
| nota_voto | DECIMAL(4,2)  |  Not Null    |Valor numérico da votação atribuído ao critério|

## 6. Votos
Registra as avaliações dadas pelos usuários aos projetos.
| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_voto | INT / UUID     |PK, Auto Increment   | Identificador único do voto registrado|
| id_usuario | INT / UUID     |FK, Not Null   | Chave estrangeira que identifica o eleitor|
| id_estandes| INT / UUID  | Not Null   |Chave estrangeira que identifica o projeto votado|
| id_criterio | INT / UUID  |  FK, Not Null    |Chave estrangeira que identifica o critério pontuado|
| nota_voto | DECIMAL(4,2)  |  Not Null    |Nota atribuída ao critério|
| data_voto | DATETIME  |  Not Null    |Data e hora exatas do registro do voto|

## 7. Ranking
Registra os projetos que foram destacados, conforme votação.

| Atributos | Tipo de Dados | Restrição | Descrição 
| ----------- | ----------- | ----------- | ----------- |
| id_ranking | INT / UUID     |PK, Auto Increment   | Identificador único do ranking|
| id_estande | INT / UUID     |FK, Unique, Not Null   | Conecta a chave estrangeira do estande|
| media_final| INT / UUID  | Not Null   |Média geral das notas calculadas para o projeto|






