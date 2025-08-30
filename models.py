from pydantic import BaseModel

class RegisterPlayerRequest(BaseModel):
    wallet_address: str
    nickname: str

class LogMatchRequest(BaseModel):
    player1: str
    player2: str
    game: str
    result: int  # 0: empate, 1: gana p1, 2: gana p2
    evidence_hash: str  # en hex
