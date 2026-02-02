# ===============================
# CONFIGURAÇÃO DO MODO DE EXECUÇÃO
# ===============================
# Alterar apenas esta linha para mudar o comportamento
MODO = "teste"  # Opções: "teste" ou "bd"

# Configuração da Base de Dados (apenas usado se MODO = "bd")
CONFIG_BD = {
    "host": "192.168.1.100",  # IP do servidor Alpine no Proxmox
    "port": 5432,
    "database": "epistemotecnica",
    "user": "leonardo",
    "password": "senha_segur"  # ATENÇÃO: Nunca commits passwords em Git!
}