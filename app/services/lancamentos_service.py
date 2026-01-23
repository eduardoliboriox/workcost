from app.repositories.lancamentos_repository import inserir_com_cargos, ferias_por_linha, cargos_por_linha
import json

def criar_lancamento(dados):
    try:
        dados = dict(dados)

        cargos = []
        for f in json.loads(dados.pop("cargos", "[]")):
            cargos.append({"cargo_id": f["cargo_id"], "quantidade": int(f["quantidade"]), "tipo": "FALTA"})
        for f in json.loads(dados.pop("ferias", "[]")):
            cargos.append({"cargo_id": f["cargo_id"], "quantidade": int(f["quantidade"]), "tipo": "FERIAS"})

        hc_padrao = int(dados["hc_padrao"])
        total_faltas = sum(c["quantidade"] for c in cargos if c["tipo"] == "FALTA")
        hc_real = max(hc_padrao - total_faltas, 0)
        dados["hc_real"] = hc_real
        dados["absenteismo"] = round((hc_padrao - hc_real) / hc_padrao * 100, 2) if hc_padrao > 0 else 0

        inserir_com_cargos(dados, cargos)
        return {"success": True, "hc_real": hc_real, "absenteismo": dados["absenteismo"]}
    except Exception as e:
        return {"success": False, "erro": str(e)}

def cargos_faltas_por_linha(linha, filtros):
    return faltas_por_cargo_e_linha(linha, filtros)

def faltas_por_linha(linha, filtros):
    return cargos_por_linha(linha, "FALTA", filtros)

def ferias_por_linha_cargos(linha, filtros):
    return cargos_por_linha(linha, "FERIAS", filtros)

