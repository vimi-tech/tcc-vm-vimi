# Manual de Configuração, Arquitetura e Deploy Cloud

Este documento detalha a infraestrutura cloud, o modelo de segurança e o funcionamento da esteira de automação (CI/CD) do projeto.

---

## 1. Configuração dos Serviços Cloud (Firebase)

### Firebase Authentication
* **Objetivo:** Controle de acesso e identidade dos usuários da aplicação.
* **Status:** Ativado no Console do Firebase.
* **Provedor Utilizado:** E-mail e Senha.
* **Integração:** O token de autenticação gerado pelo Firebase Auth é utilizado pelo Firestore para validar as permissões de leitura e escrita.

### Firebase Firestore (Banco de Dados)
* **Região de Instalação:** `southamerica-east1` (São Paulo) para menor latência.
* **Modo Inicial:** Configurado em **Modo Bloqueado** para garantir segurança total por padrão.
* **Regras de Segurança:** O banco foi configurado para rejeitar qualquer requisição anônima. Apenas usuários validados pelo Firebase Authentication possuem permissão de acesso.

---

## 2. Segurança e Configuração das Máquinas (GitHub Secrets)

Para que o GitHub Actions gerencie o deploy e interaja com a nuvem com segurança, as credenciais não ficam expostas no código.

1. Foi gerada uma **Chave Privada JSON** no console do Firebase (*Configurações do Projeto > Contas de Serviço > Gerar nova chave privada*).
2. O conteúdo desse arquivo JSON foi salvo no repositório do GitHub em `Settings > Secrets and Variables > Actions` com o nome:
   * `FIREBASE_SERVICE_ACCOUNT`

---

## 3. Esteira de Automação (CI/CD) e Qualidade

A esteira de automação foi desenhada para garantir que o código e a documentação mantenham um padrão de qualidade antes de qualquer alteração ir para produção.

### Workflow de Validação de Documentação (`docs-check.yml`)
* **Gatilho:** Disparado automaticamente a cada `push` ou `pull_request` nas branches `main` ou `master`.
* **Funcionamento:** O runner do GitHub (máquina virtual Ubuntu) faz o checkout do código e executa o `markdownlint-cli2-action`.
* **Critério de Sucesso:** Se houver erros de formatação nos arquivos `.md` (como links quebrados ou falta de títulos), o build falha, impedindo o merge de documentações incompletas ou mal formatadas.