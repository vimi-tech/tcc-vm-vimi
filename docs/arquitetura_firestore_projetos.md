# Arquitetura do Sistema: Conexão Firestore e Cadastro de Projetos por Turma

## 1. Visão Geral da Arquitetura
O sistema segue os princípios de **Clean Architecture** e **SOLID**, desacoplando a infraestrutura do banco de dados (Cloud Firestore) das regras de negócio e controladores web.

```
app/
├── config/
│   ├── firebase.py               # Singleton de conexão com o Firebase (projeto: tccfeirascore)
│   └── __init__.py
├── models/
│   ├── project.py                # Entidade de Domínio Project (vinculada a uma Turma)
│   ├── user.py                   # Entidade de Domínio User
│   └── __init__.py
├── repositories/
│   ├── project_repositories.py   # Repositório de Projetos no Firestore (coleção: estandes)
│   └── user_repositories.py      # Repositório de Usuários no Firestore
├── services/
│   ├── media_service.py          # Gestão de upload de mídias (Cloudinary e Local)
│   ├── project_service.py        # Regras de negócio de projetos e unicidade de turma
│   └── auth_services.py          # Regras de autenticação
└── controllers/
    ├── project_controller.py     # Blueprint e rotas de cadastro e listagem de projetos
    ├── auth_controller.py        # Blueprint de login e registro
    └── home_controller.py        # Blueprint da página inicial
```

---

## 2. Conexão com o Firebase Firestore
* **Projeto no Firebase Console:** [`tccfeirascore`](https://console.firebase.google.com/project/tccfeirascore)
* **Módulo de Conexão:** `app/config/firebase.py`
* **Estratégia de Resolução de Credenciais:**
  1. Variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS` ou `FIREBASE_CREDENTIALS` apontando para o arquivo de chave.
  2. Variável de ambiente `FIREBASE_CREDENTIALS_JSON` contendo o JSON da Service Account diretamente.
  3. Arquivo local `serviceAccountKey.json` na raiz ou em `/etc/secrets/serviceAccountKey.json`.
  4. Fallback com Application Default Credentials (ADC) e `projectId='tccfeirascore'`.

---

## 3. Modelo de Domínio: Projeto Conectado a uma Turma
No domínio de negócio da feira:
* Cada **Turma** é responsável por exatamente **1 Projeto/Estande**.
* A entidade `Project` contém:
  * `id`: Identificador único do documento no Firestore.
  * `turma`: Nome ou código da turma (ex: "3º B", "Turma 45").
  * `turma_busca`: Turma em minúsculas para consultas seguras e sem case-sensitivity.
  * `nome`: Nome ou título do projeto.
  * `resumo`: Descrição explicativa do projeto.
  * `midias`: Lista de URLs ou nomes de arquivos de fotos e vídeos.
  * `criadoEm`: Timestamp do servidor.

---

## 4. Fluxo de Cadastro e Uso da Rota `/descricaoprojeto`
1. O aluno acessa `/estandelogin`, insere o código da sua turma e é redirecionado para `/descricaoprojeto?turma=Turma%20XX`.
2. A rota `/descricaoprojeto` pré-preenche o campo da turma no formulário.
3. Ao submeter o formulário (POST):
   * O `ProjectService` valida os campos obrigatórios.
   * O `ProjectRepository` confere se a turma já possui um projeto cadastrado no Firestore.
   * O `MediaService` processa as mídias (Cloudinary ou pasta local).
   * O projeto é persistido na coleção do Firestore.
   * Caso ocorra erro de persistência, as mídias salvas são apagadas para evitar lixo no storage.
