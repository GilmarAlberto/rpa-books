# rpa-books

Robô de RPA em Python que abre o site [Books to Scrape](https://books.toscrape.com/) em um navegador, percorre as 50 páginas do catálogo, coleta **título, preço e estoque** dos 1.000 livros e salva tudo em um banco **SQLite**, sem duplicar registros e atualizando preço e estoque quando mudam. Cada execução fica registrada em um arquivo de log, inclusive as falhas.

## O que o robô faz

1. Abre o Chromium em modo invisível (headless) com o **Playwright**.
2. Lê os 20 livros de cada página e clica em "next" até chegar à última (50 páginas, cerca de 40 segundos).
3. Compara com o banco `livros.db`: insere os livros novos, atualiza preço e estoque dos que mudaram e ignora os que estão iguais.
4. Registra o início, o resultado e qualquer erro em `robo.log`.

## Tecnologias

- Python 3.14
- Playwright (automação de navegador)
- SQLite (banco de dados local, já incluso no Python)
- logging (biblioteca padrão do Python)

## Como instalar

Pré-requisito no Linux (Debian/Ubuntu): o pacote `python3-venv` correspondente à sua versão do Python.

```bash
git clone https://github.com/GilmarAlberto/rpa-books.git
cd rpa-books
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Como usar

```bash
python robo.py
```

Saída na primeira execução:

```
Coletados: 1000 | novos: 1000 | atualizados: 0
```

Saída se rodar de novo (os livros já estão no banco, então nada é duplicado):

```
Coletados: 1000 | novos: 0 | atualizados: 0
```

Se o preço ou o estoque de algum livro mudar no site, ele é atualizado, e o log registra o antes e o depois:

```
Coletados: 1000 | novos: 0 | atualizados: 1
```

```
INFO Atualizado: A Light in the Attic | £1.00 -> £51.77 | In stock -> In stock
```

Para conferir quantos livros há no banco:

```bash
python -c "import sqlite3; print(sqlite3.connect('livros.db').execute('SELECT COUNT(*) FROM livros').fetchone()[0])"
```

## Testando o tratamento de erros

A URL pode ser trocada pela variável de ambiente `ROBO_URL`. Com um endereço inexistente, o robô falha de forma controlada:

```bash
ROBO_URL="https://site-que-nao-existe.invalid/" python robo.py
```

```
Erro! Veja os detalhes em robo.log
```

O robô encerra com código de saída `1`, e o log registra a falha com o motivo completo:

```
2026-10-03 09:00:51,858 INFO Início da execução (URL: https://site-que-nao-existe.invalid/)
2026-10-03 09:00:52,467 ERROR Falha na execução
...
playwright._impl._errors.Error: Page.goto: net::ERR_NAME_NOT_RESOLVED at https://site-que-nao-existe.invalid/
```

## Decisões técnicas

- **Sem duplicação, com atualização:** a URL do livro é a chave primária da tabela. Para cada livro coletado, o robô consulta o banco: se não existe, insere; se o preço ou o estoque mudou, atualiza e preenche `atualizado_em`; se está igual, não mexe. Assim, rodar o robô várias vezes é seguro (execução idempotente) e o banco reflete o site.
- **URL como identificador, não o título:** o catálogo tem dois livros diferentes chamados "The Star-Touched Queen". Com o título como chave, um deles seria descartado sem aviso; a URL é única para cada livro.
- **Paginação pelo botão "next":** o robô não assume que existem 50 páginas; segue o link até ele sumir, então continua funcionando se o catálogo crescer ou diminuir.
- **Log em arquivo:** cada execução deixa rastro em `robo.log` com data e hora, o que é essencial para acompanhar um robô que roda sem ninguém olhando.
- **Falha controlada:** qualquer erro é capturado, registrado com o traceback completo e devolvido como código de saída `1`, o que permite que um agendador (como o cron) perceba que algo deu errado.
- **Configuração por variável de ambiente:** a URL pode ser trocada sem alterar o código.
- **Datas no horário local:** `coletado_em` e `atualizado_em` usam `datetime('now', 'localtime')`, porque o `CURRENT_TIMESTAMP` do SQLite grava em UTC (3 horas à frente de Brasília) e não bateria com o log.
- **Arquivos gerados fora do Git:** `livros.db` e `robo.log` estão no `.gitignore`.

## Estrutura

```
rpa-books/
├── robo.py           # o robô: coleta, salva e registra no log
├── requirements.txt  # dependências
└── README.md
```

## Próximos passos

- Agendar a execução automática com o cron.
