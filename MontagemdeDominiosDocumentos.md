# Montagem de Domínios de Negócios para orientação dos projetos Finais [Documentos]

## 1. Usuário
O que acontece: Esta tabela armazena os dados cadastrais de todas as pessoas que navegam pelo sistema e que precisam fazer login para conseguir votar nos projetos.

Atributos principais:

• id_usuario: Identificador único (chave primária).

• email: E-mail usado para autenticação (único e obrigatório).

• codigo_confirmacao: Código enviado por e-mail para validar e ativar o acesso.

• cpf: Utilizado para validação única de cada pessoa.

## 2. Entrar como turma
O que acontece: Representa a turma de alunos responsável por criar e gerenciar um projeto/estande. O acesso a essa área é liberado por meio de um código específico de validação.

• Atributos principais:

• id_turma: Identificador único da turma.

• codigo_acesso: Código que a turma insere para conseguir cadastrar o seu projeto.

## 3. Cadastro dos estandes
O que acontece: Guarda as informações detalhadas sobre o projeto submetido por uma turma. É esta tabela que alimenta a página principal de exibição dos estandes.

Atributos principais:

• id_estande: Identificador único do projeto.

• id_turma: Faz a ligação (relacionamento) indicando qual turma é dona daquele estande.

• nome_projeto e descricao: Nome e texto explicativo do trabalho.

• url_foto e url_video: Arquivos multimídia obrigatórios do estande.

## 4. Página de Estandes
O que acontece: Na prática, esta tabela reflete a mesma estrutura de dados da tabela anterior (Cadastro dos estandes), servindo de forma consolidada para estruturar e exibir os estandes cadastrados pelos alunos na interface pública da página.

## 5. Critérios para avaliação (votação)
O que acontece: Armazena as perguntas ou quesitos que os jurados/usuários devem avaliar para definir a pontuação e o pódio dos projetos.

Atributos principais:

• id_criterio: Identificador único do critério de avaliação.

• id_estandes: Chave estrangeira que vincula o critério ao projeto avaliado.

• nota_voto: O valor numérico atribuído àquele critério específico.

## 6. Votos
O que acontece: É a tabela transacional mais importante para o processo de votação. Ela registra, de forma detalhada, cada avaliação que um usuário fez em cima de um projeto, considerando os critérios estabelecidos.

Atributos principais:

• id_voto: Identificador único de cada voto gerado.

• id_usuario: Identifica quem votou (o eleitor).

• id_estandes: Identifica qual projeto recebeu o voto.

• id_criterio: Identifica qual critério está sendo pontuado.

• nota_voto e data_voto: O valor da nota dada e o registro exato de quando o voto foi efetuado.
