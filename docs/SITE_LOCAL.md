# Consulta web local

O site é estático e lê o dataset JSON com `fetch()`. Por isso, deve ser servido
por HTTP em vez de abrir `index.html` diretamente.

## Iniciar

```bash
python3 -m http.server 8000 --directory public
```

Acesse `http://127.0.0.1:8000/` no navegador.

## Testes

```bash
npm run test:web
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

O campo de pesquisa por nome da cidade funciona em conjunto com os filtros de
cidade, zona e seção. A pesquisa ignora diferenças entre maiúsculas e acentos.

## Filtros compartilháveis

Os filtros podem ser combinados e refletidos na URL:

```text
http://127.0.0.1:8000/?q=natividade&cidade=94811&zona=19&secao=81
```

Parâmetros inválidos são ignorados e removidos durante a inicialização.
