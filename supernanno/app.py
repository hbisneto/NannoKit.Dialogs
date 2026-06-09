from dialogs import messagebox 

def resposta(btn):
    print(f"Usuário clicou em: {btn}")

messagebox.show(
    "O arquivo já existe. Deseja sobrescrever?",
    "Aviso",
    messagebox.buttons.RETRY_CANCEL,
    type=messagebox.type.SUCCESS,
    callback=resposta
)