class UsuarioRegistroMixin:
    """Llena el campo user del ModeloBase con el usuario conectado."""
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)