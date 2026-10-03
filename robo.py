from playwright.sync_api import sync_playwright

URL = "https://books.toscrape.com/"


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
            livros.append({"titulo": titulo, "preco": preco, "estoque": estoque})
        navegador.close()
    return livros


if __name__ == "__main__":
    for livro in coletar():
        print(livro["titulo"], "|", livro["preco"], "|", livro["estoque"])
