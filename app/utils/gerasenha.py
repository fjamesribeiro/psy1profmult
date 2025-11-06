from app.services.auth_service import get_password_hash

# Gere o hash da senha
senha_hash = get_password_hash("psyconexa")
print(senha_hash)

# Atualize no banco manualmente ou via script:
# UPDATE profissional SET senha_hash = 'hash_gerado' WHERE id = 1;
