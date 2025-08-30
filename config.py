import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# URLs oficiales de Lisk Sepolia
RPC_URLS = [
    "https://rpc.sepolia-api.lisk.com",
    "https://sepolia-rpc.lisk.com",
    "https://lisk-sepolia.drpc.org"
]

RPC_URL = os.getenv("RPC_URL", RPC_URLS[0])


def connect_to_lisk():
    """Intenta conectar a diferentes RPC endpoints de Lisk Sepolia"""
    urls_to_try = [RPC_URL] + [url for url in RPC_URLS if url != RPC_URL]

    for url in urls_to_try:
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))

            # Verificar conexión con una llamada simple
            chain_id = w3.eth.chain_id
            if chain_id == 4202:  # Lisk Sepolia Chain ID
                print(f"✅ Conectado exitosamente a Lisk Sepolia: {url}")
                print(f"   Chain ID: {chain_id}")
                return w3
            else:
                print(
                    f"⚠️  Conectado a {url} pero Chain ID incorrecto: {chain_id}")

        except Exception as e:
            print(f"❌ Error conectando a {url}: {str(e)[:100]}...")
            continue

    print("❌ No se pudo conectar a ningún nodo de Lisk Sepolia")
    return None


# Intentar conexión
w3 = connect_to_lisk()

# Si no se puede conectar, crear un objeto Web3 mock para desarrollo
if w3 is None:
    print("🔧 Modo desarrollo: creando conexión mock...")
    w3 = Web3()  # Sin provider, para desarrollo local
