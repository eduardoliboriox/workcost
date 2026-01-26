from app.repositories import hc_linhas_repository


def listar():
    return hc_linhas_repository.listar()


def salvar(dados):
    try:
        hc_linhas_repository.inserir(
            dados["setor"],
            dados["linha"],
            int(dados["hc_padrao"])
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def excluir(id_):
    try:
        hc_linhas_repository.excluir(id_)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
