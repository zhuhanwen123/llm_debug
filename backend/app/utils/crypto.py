def decrypt_api_key(api_key_enc: str | None, master_key: str) -> str:
    if not api_key_enc:
        return ""

    # TODO: replace with real encryption/decryption based on MASTER_KEY.
    if api_key_enc.startswith("plain:"):
        return api_key_enc.removeprefix("plain:")

    return api_key_enc
