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
        paginas = 1
        while True:
            for item in pagina.query_selector_all("article.product_pod"):
                link = item.query_selector("h3 a")
                url = link.evaluate("e => e.href")  # endereço completo do livro
                titulo = link.get_attribute("title")
                preco = item.query_selector("p.price_color").inner_text()
                estoque = item.query_selector("p.availability").inner_text().strip()
                livros.append((url, titulo, preco, estoque))
            # Sem botão "next" = última página
            proxima = pagina.query_selector("li.next a")
            if proxima is None:
                break
            proxima.click()
            pagina.wait_for_load_state()
            paginas += 1
        navegador.close()
    logging.info("Páginas percorridas: %d", paginas)
    return livros


def salvar(livros):
    con = sqlite3.connect(BANCO)
    # A URL é a chave: há títulos repetidos no catálogo
    con.execute(
        "CREATE TABLE IF NOT EXISTS livros ("
        "url TEXT PRIMARY KEY, titulo TEXT, preco TEXT, estoque TEXT, "
        "coletado_em TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    novos = 0
    for livro in livros:
        cur = con.execute(
            "INSERT OR IGNORE INTO livros (url, titulo, preco, estoque) VALUES (?, ?, ?, ?)",
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
