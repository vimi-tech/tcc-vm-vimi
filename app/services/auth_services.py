class AuthService:
    def __init__(self):
        # Inicialize seus repositórios aqui se necessário
        pass

    def register_user(self, nome, email, senha, confirma_senha):
        if not nome or not email or not senha:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if senha != confirma_senha:
            raise ValueError("As senhas não coincidem.")

        try:
            # Lógica de criação do usuário
            # self.user_repo.save_user_data(uid, email, codigo_email)
            return True, "Cadastro feito com sucesso! Agora você pode votar nos projetos"
        except Exception as e:
            raise Exception(f"Erro ao criar conta: {str(e)}")