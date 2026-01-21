from app.repositories import cargos_repository

def listar():
    return cargos_repository.listar()

def listar_por_area(area):
    return cargos_repository.listar_por_area(area)

def cadastrar(dados):
    cargos_repository.inserir(
        dados["nome"],
        dados["area"]
    )
    return {"sucesso": True}

def atualizar(dados):
    cargos_repository.atualizar(
        dados["id"],
        dados["nome"],
        dados["area"]
    )
    return {"sucesso": True}

def excluir(dados):
    cargos_repository.excluir(dados["id"])
    return {"sucesso": True}
