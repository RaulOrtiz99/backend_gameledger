from fastapi import FastAPI, HTTPException
from models import RegisterPlayerRequest, LogMatchRequest
# Importación condicional para evitar que falle al inicio
try:
    from config import w3
    W3_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Advertencia: No se pudo importar config.py: {e}")
    w3 = None
    W3_AVAILABLE = False
import os

app = FastAPI(
    title="GamerLedger Backend",
    description="API para registrar jugadores y partidas en Lisk Sepolia",
    version="0.1.0"
)

PLAYER_PROFILE_ADDR = os.getenv("PLAYER_PROFILE_ADDRESS")
MATCH_HISTORY_ADDR = os.getenv("MATCH_HISTORY_ADDRESS")


@app.get("/")
def home():
    return {"message": "Bienvenido al backend de GamerLedger"}


@app.get("/health")
def health_check():
    if not W3_AVAILABLE:
        return {
            "status": "degraded",
            "message": "Web3 connection not available",
            "network": "Lisk Sepolia",
            "chain_id": os.getenv("CHAIN_ID"),
            "rpc_connected": False,
            "player_profile": PLAYER_PROFILE_ADDR,
            "match_history": MATCH_HISTORY_ADDR
        }

    return {
        "status": "ok",
        "network": "Lisk Sepolia",
        "chain_id": os.getenv("CHAIN_ID"),
        "rpc_connected": w3.is_connected() if w3 else False,
        "player_profile": PLAYER_PROFILE_ADDR,
        "match_history": MATCH_HISTORY_ADDR
    }


@app.get("/contracts")
def get_contract_addresses():
    return {
        "PlayerProfile": PLAYER_PROFILE_ADDR,
        "MatchHistory": MATCH_HISTORY_ADDR,
        "Tournament": os.getenv("TOURNAMENT_ADDRESS"),
        "network": "lisk:sepolia",
        "rpc": os.getenv("RPC_URL")
    }


@app.post("/register-player")
def register_player(data: RegisterPlayerRequest):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    if not w3.is_address(data.wallet_address):
        raise HTTPException(400, "Dirección Ethereum inválida")

    addr = w3.to_checksum_address(data.wallet_address)

    return {
        "success": True,
        "message": "Datos validados. Registra en blockchain desde Flutter.",
        "contract_address": PLAYER_PROFILE_ADDR,
        "function": "register_player",
        "args": [data.nickname],
        "network": "lisk:sepolia"
    }


@app.post("/log-match")
def log_match(data: LogMatchRequest):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    if not w3.is_address(data.player1) or not w3.is_address(data.player2):
        raise HTTPException(400, "Una de las direcciones es inválida")

    player1 = w3.to_checksum_address(data.player1)
    player2 = w3.to_checksum_address(data.player2)

    if data.result not in [0, 1, 2]:
        raise HTTPException(
            400, "Resultado inválido. Usa: 0=empate, 1=gana p1, 2=gana p2")

    return {
        "success": True,
        "contract_address": MATCH_HISTORY_ADDR,
        "function": "log_match",
        "args": [
            player1,
            player2,
            data.game,
            data.result,
            w3.eth.get_block("latest")["timestamp"] if w3 else 0,
            bytes.fromhex(data.evidence_hash.replace("0x", ""))
        ],
        "gas_estimate": 250000,
        "network": "lisk:sepolia",
        "message": "Usa estos datos en Flutter con web3dart para firmar"
    }
