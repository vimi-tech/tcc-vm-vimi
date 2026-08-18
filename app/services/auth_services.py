from app.repositories.user_repositories import UserRepository
class AuthService: 
    def __init___(self):
        self.user_repo= UserRepository()
    
    def register_user(email: str, codigo_email: str):
        if not email or not codigo_email:
            raise ValueError("Todos os campos são obrigatórios.")

        if codigo_email != codigo_email:
            raise ValueError("O código não coincide.")

        try:
            uid = self.user_repo.create_user_auth(email, codigo_email)

            self.user_repo.save_user_data(uid, email, codigo_email)

            return True, "Cadastro feito com sucesso!Agora você pode votar nos projetos"
            except Exception as e:
                raise Exception(f"Erro ao criar conta: {str(e)}")
