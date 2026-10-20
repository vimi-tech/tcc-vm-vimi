from app.repositories.user_repositories import UserRepository


class AuthService:
    def __init__(self, user_repo=None):
        self.user_repo = user_repo or UserRepository()

    def register_user(self, nome, email, senha, confirma_senha):
        if not nome or not email or not senha:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if senha != confirma_senha:
            raise ValueError("As senhas não coincidem.")

        try:
            uid = self.user_repo.create_user_auth(
                email=email,
                password=senha,
                display_name=nome
            )
            self.user_repo.save_user_data(uid=uid, nome=nome, email=email)
            return True, "Cadastro feito com sucesso! Agora você pode votar nos projetos"
        except Exception as e:
            raise Exception(f"Erro ao criar conta: {str(e)}")