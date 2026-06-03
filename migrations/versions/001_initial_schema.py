"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-03
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # categorias
    op.create_table(
        "categorias",
        sa.Column("id", sa.SmallInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_categorias_slug"),
    )

    # lojas
    op.create_table(
        "lojas",
        sa.Column("id", sa.SmallInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("dominio_base", sa.String(200), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_lojas_slug"),
    )
    op.create_index("ix_lojas_dominio", "lojas", ["dominio_base"])

    # usuarios
    op.create_table(
        "usuarios",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("nome", sa.String(200), nullable=True),
        sa.Column("whatsapp", sa.String(20), nullable=True),
        sa.Column("push_token", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("atualizado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )

    # produtos
    op.create_table(
        "produtos",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("url_canonica", sa.Text(), nullable=False),
        sa.Column("loja_id", sa.SmallInteger(), nullable=False),
        sa.Column("categoria_id", sa.SmallInteger(), nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("imagem_url", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("atualizado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["loja_id"], ["lojas.id"]),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("CREATE UNIQUE INDEX uq_produtos_url_loja ON produtos(loja_id, md5(url_canonica))")
    op.execute("CREATE INDEX ix_produtos_categoria ON produtos(categoria_id) WHERE ativo = true")

    # coletas — série temporal de preços (tabela de maior volume)
    op.create_table(
        "coletas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("produto_id", sa.BigInteger(), nullable=False),
        sa.Column("coletado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("preco_atual", sa.Numeric(12, 2), nullable=False),
        sa.Column("preco_original", sa.Numeric(12, 2), nullable=True),
        sa.Column("desconto_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("score_ico", sa.Numeric(5, 2), nullable=True),
        sa.Column("disponivel", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("fonte_raw", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("preco_atual >= 0", name="ck_coletas_preco_atual"),
        sa.CheckConstraint("desconto_pct BETWEEN 0 AND 100", name="ck_coletas_desconto"),
        sa.CheckConstraint("score_ico BETWEEN 0 AND 100", name="ck_coletas_score"),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("CREATE INDEX ix_coletas_produto_tempo ON coletas(produto_id, coletado_em DESC)")
    op.execute("CREATE INDEX ix_coletas_score ON coletas(score_ico DESC) WHERE disponivel = true")
    op.execute("CREATE INDEX ix_coletas_fonte_raw ON coletas USING gin(fonte_raw) WHERE fonte_raw IS NOT NULL")

    # alertas — assinaturas de usuários (Fase 5)
    op.create_table(
        "alertas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("produto_id", sa.BigInteger(), nullable=False),
        sa.Column("preco_alvo", sa.Numeric(12, 2), nullable=True),
        sa.Column("score_ico_alvo", sa.Numeric(5, 2), nullable=True),
        sa.Column("desconto_alvo_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("canal", sa.String(20), nullable=False, server_default=sa.text("'email'")),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ultima_disparado_em", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("preco_alvo > 0", name="ck_alertas_preco_alvo"),
        sa.CheckConstraint("score_ico_alvo BETWEEN 0 AND 100", name="ck_alertas_score"),
        sa.CheckConstraint("canal IN ('email', 'whatsapp', 'push')", name="ck_alertas_canal"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("CREATE INDEX ix_alertas_produto_ativo ON alertas(produto_id) WHERE ativo = true")

    # seed: categorias iniciais
    op.execute(
        "INSERT INTO categorias (slug, nome) VALUES "
        "('eletronicos', 'Eletrônicos'), "
        "('seguranca', 'Segurança'), "
        "('viagens', 'Viagens'), "
        "('cruzeiros', 'Cruzeiros')"
    )


def downgrade() -> None:
    op.drop_table("alertas")
    op.drop_table("coletas")
    op.drop_table("produtos")
    op.drop_table("usuarios")
    op.drop_table("lojas")
    op.drop_table("categorias")
