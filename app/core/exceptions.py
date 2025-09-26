class AppBaseError(Exception):
    """Base exception para a aplicação"""
    def __init__(self, message="Erro na aplicação", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

class SessionError(AppBaseError):
    def __init__(self, message="Erro na gestão de sessão"):
        super().__init__(message, 500)


class NotFoundError(AppBaseError):
    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)
