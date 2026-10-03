import logging
import os
import sqlite3

from playwright.sync_api import sync_playwright

URL = os.environ.get("ROBO_URL", "https://books.toscrape.com/")
BANCO = "livros.db"

logging.basicConfig(
    filename="robo.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


def coletar():
    livros = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(URL, timeout=30000)
        for item in pagina.query_selector_all("article.product_pod"):
            titulo = item.query_selector("h3 a").get_attribute("title")
            preco = item.query_selector("p.price_color").inner_text()
            estoque = item.query_selector("p.availability").inner_text().strip()
            livros.append((titulo, preco, estoque))
        navegador.close()
    return livros


def salvar(livros):
    con = sqlite3.connect(BANCO)
    con.execute(
        "CREATE TABLE IF NOT EXISTS livros ("
        "titulo TEXT PRIMARY KEY, preco TEXT, estoque TEXT, "
        "coletado_em TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    novos = 0
    for livro in livros:
        cur = con.execute(
            "INSERT OR IGNORE INTO livros (titulo, preco, estoque) VALUES (?, ?, ?)",
            livro,
        )
        novos += cur.rowcount
    con.commit()
    con.close()
    return novos


if __name__ == "__main__":
    try:
        logging.info("Início da execução (URL: %s)", URL)
        livros = coletar()
        novos = salvar(livros)
        logging.info("Coletados: %d | novos no banco: %d", len(livros), novos)
        print(f"Coletados: {len(livros)} | novos no banco: {novos}")
    except Exception:
        logging.exception("Falha na execução")
        print("Erro! Veja os detalhes em robo.log")
        raise SystemExit(1)
