"""Validação e normalização da entrada HTTP (mensagens de erro do contrato original)."""
from src.constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    StatusPedido,
)
from src.errors import ValidationError


def _is_number(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _is_int(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _exigir_dict(dados, mensagem="Dados inválidos"):
    if not isinstance(dados, dict) or not dados:
        raise ValidationError(mensagem)
    return dados


def validar_produto(dados):
    dados = _exigir_dict(dados)
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"),
                            ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome, preco, estoque = dados["nome"], dados["preco"], dados["estoque"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not _is_number(preco):
        raise ValidationError("Preço inválido")
    if not _is_int(estoque):
        raise ValidationError("Estoque inválido")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição inválida")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}


def validar_filtros_busca(args):
    filtros = {"termo": args.get("q", ""), "categoria": args.get("categoria") or None}
    for campo in ("preco_min", "preco_max"):
        valor = args.get(campo)
        try:
            filtros[campo] = float(valor) if valor else None
        except ValueError:
            raise ValidationError("Filtro " + campo + " inválido") from None
    return filtros


def _texto(dados, campo):
    valor = dados.get(campo, "")
    return valor.strip() if isinstance(valor, str) else ""


def validar_usuario(dados):
    dados = _exigir_dict(dados)
    nome, email, senha = _texto(dados, "nome"), _texto(dados, "email"), dados.get("senha", "")
    if not nome or not email or not isinstance(senha, str) or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    mensagem = "Email e senha são obrigatórios"
    dados = _exigir_dict(dados, mensagem)
    email, senha = _texto(dados, "email"), dados.get("senha", "")
    if not email or not isinstance(senha, str) or not senha:
        raise ValidationError(mensagem)
    return {"email": email, "senha": senha}


def validar_pedido(dados):
    dados = _exigir_dict(dados)
    usuario_id, itens = dados.get("usuario_id"), dados.get("itens")
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not _is_int(usuario_id):
        raise ValidationError("Usuario ID inválido")
    if not isinstance(itens, list) or not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    itens_validos = []
    for item in itens:
        if not isinstance(item, dict) or not _is_int(item.get("produto_id")) or not _is_int(item.get("quantidade")):
            raise ValidationError("Cada item deve ter produto_id e quantidade inteiros")
        if item["quantidade"] <= 0:
            raise ValidationError("Quantidade deve ser maior que zero")
        itens_validos.append({"produto_id": item["produto_id"], "quantidade": item["quantidade"]})
    return {"usuario_id": usuario_id, "itens": itens_validos}


def validar_status_pedido(dados):
    status = dados.get("status") if isinstance(dados, dict) else None
    if status not in StatusPedido.TODOS:
        raise ValidationError("Status inválido")
    return status


def validar_sql(dados):
    sql = dados.get("sql") if isinstance(dados, dict) else None
    if not isinstance(sql, str) or not sql.strip():
        raise ValidationError("Query não informada")
    return sql
