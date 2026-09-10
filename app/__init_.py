class AuthService:
    def __init__(self):
        pass

    def register_user(self, nome, email, senha, confirma_senha):
        if not nome or not email or not senha:
            raise ValueError("Preencha todos os campos obrigatórios.")
            
        if senha != confirma_senha:
            raise ValueError("As senhas não coincidem.")

        try:
            # Coloque aqui a sua lógica de cadastro
            return True, "Usuário cadastrado com sucesso!"
        except Exception as e:
            raise Exception(f"Erro no cadastro: {str(e)}")