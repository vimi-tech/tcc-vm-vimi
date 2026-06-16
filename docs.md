# Esteira de Automação e Infraestrutura Cloud com Firebase

Este repositório contém a implementação de um fluxo completo de deploy e qualidade para a nuvem utilizando os serviços do Firebase e automação via GitHub Actions.

## 🚀 Tecnologias Utilizadas
* **Firebase Firestore:** Banco de dados NoSQL estruturado em Modo Bloqueado.
* **Firebase Authentication:** Controle e gerenciamento de acessos de usuários.
* **GitHub Actions:** Automação de processos (CI/CD) e checagem de qualidade.
* **Markdownlint:** Linter para validação e manutenção das boas práticas de documentação.

## 📂 Estrutura do Repositório
* `.github/workflows/docs-check.yml`: Configuração da esteira automatizada que valida a documentação.
* `docs/deploy-guide.md`: Manual oficial detalhando a infraestrutura e segurança do projeto.

## 🛠️ Como Testar a Automação
Para testar a Action de validação da documentação:
1. Crie uma nova branch ou faça uma alteração nos arquivos `.md`.
2. Execute os comandos de Git:
   ```bash
   git add .
   git commit -m "docs: atualizando manual de deploy"
   git push origin main
