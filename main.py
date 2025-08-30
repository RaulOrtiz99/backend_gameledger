# backend/main.py

from fastapi import FastAPI, HTTPException
from models import RegisterPlayerRequest, LogMatchRequest
from config import w3, W3_AVAILABLE
import os
import json

app = FastAPI(
    title="GamerLedger Backend",
    description="API para registrar jugadores y partidas en Lisk Sepolia",
    version="0.1.0"
)

PLAYER_PROFILE_ADDR = os.getenv("PLAYER_PROFILE_ADDRESS")
MATCH_HISTORY_ADDR = os.getenv("MATCH_HISTORY_ADDRESS")
TOURNAMENT_ADDR = os.getenv("TOURNAMENT_ADDRESS")

CHAIN_ID = 4202

# 🔐 Autenticación básica (JWT en producción)
# Para MVP: usamos wallet address como ID

# 🎯 Endpoints del flujo


@app.post("/auth")
def auth_player(req: RegisterPlayerRequest):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    if not w3.is_address(req.wallet_address):
        raise HTTPException(400, "Dirección inválida")

    addr = w3.to_checksum_address(req.wallet_address)

    return {
        "success": True,
        "message": "Wallet verificada",
        "address": addr,
        "chain": "lisk:sepolia"
    }


@app.post("/verify-stats")
def verify_stats(game: str, player_id: str):
    # Aquí podrías llamar a una API externa (ej: Fortnite Tracker)
    # Por ahora, solo simula una verificación exitosa
    return {
        "success": True,
        "verified": True,
        "game": game,
        "player_id": player_id,
        "timestamp": int(time.time())
    }


@app.post("/submit-proof")
def submit_proof(req: LogMatchRequest):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    try:
        tx_data = prepare_transaction(
            contract_addr=MATCH_HISTORY_ADDR,
            abi_path="contracts/MatchHistory.json",
            function="log_match",
            args=[
                req.player1,
                req.player2,
                req.game,
                req.result,
                w3.eth.get_block("latest")["timestamp"],
                bytes.fromhex(req.evidence_hash.replace("0x", ""))
            ]
        )
        return {
            "success": True,
            "message": "Prueba lista para firmar",
            "transaction": tx_data
        }
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")


@app.get("/profile/{address}")
def get_profile(address: str):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    if not w3.is_address(address):
        raise HTTPException(400, "Dirección inválida")

    checksum_addr = w3.to_checksum_address(address)

    # Aquí podrías combinar datos de BD + blockchain
    nickname = get_nickname_from_contract(checksum_addr)
    total_matches = 73
    verified_matches = 41
    rewards = [
        {"type": "token", "amount": 10, "tx_hash": "0xabc..."},
    ]

    return {
        "address": checksum_addr,
        "nickname": nickname,
        "total_matches": total_matches,
        "verified_matches": verified_matches,
        "rewards": rewards
    }


@app.post("/mint-token")
def mint_token(winner_address: str):
    if not W3_AVAILABLE or not w3:
        raise HTTPException(503, "Servicio Web3 no disponible")

    try:
        tx_data = prepare_transaction(
            contract_addr=TOURNAMENT_ADDR,
            abi_path="contracts/Tournament.json",
            function="declare_winner",
            # tournamentId, winner
            args=[1, w3.to_checksum_address(winner_address)]
        )
        return {
            "success": True,
            "message": "Transacción lista para mintear recompensa",
            "transaction": tx_data
        }
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")


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
        "Tournament": TOURNAMENT_ADDR,
        "network": "lisk:sepolia",
        "rpc": os.getenv("RPC_URL")
    }
