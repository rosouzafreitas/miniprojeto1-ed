# Mini Projeto: Media Player

Player de mídia simulado em Python. A interação acontece pelo terminal e usa somente a biblioteca padrão.

## Requisitos

Python 3.9 ou superior. Os testes usam `unittest`, que já acompanha o Python.

## Executar

Abra o terminal na pasta que contém o diretório `mediap` e execute:

```text
python -m mediap.main
```

No Windows, dependendo da instalação, use `py -m mediap.main`.

## Comandos

```text
library load mediap/library.json
library list
library list --by rating
library list --by title
library list --by artist
playlist new nome
playlist add 1
playlist remove 2
playlist show
play
next
prev
enqueue 5
queue show
history
smart-shuffle 5
save estado.json
load estado.json
help
quit
```

As posições exibidas na playlist começam em 1. O mesmo número deve ser usado em `playlist remove`.

## Exemplo de sessão

```text
mediap> library load mediap/library.json
Biblioteca carregada: 10 faixas.
mediap> playlist new favoritas
Playlist "favoritas" criada.
mediap> playlist add 1
mediap> playlist add 2
mediap> playlist show
> 1. Águas de Março — Elis Regina (3:32)
  2. Construção — Chico Buarque (6:21)
mediap> play
>>> Tocando: "Águas de Março" — Elis Regina (3:32)
mediap> enqueue 5
mediap> next
>>> Tocando: "Asa Branca" — Luiz Gonzaga (2:45)
mediap> next
>>> Tocando: "Construção" — Chico Buarque (6:21)
mediap> quit
```

## Estruturas e regras

A playlist usa uma lista duplamente encadeada própria, com cursor. Avançar ou retroceder o cursor custa O(1). A fila usa `collections.deque`, e o histórico usa outro deque com capacidade máxima de 20 execuções. As músicas da fila imediata são removidas ao tocar e não movem o cursor da playlist.

O smart-shuffle insere todas as faixas em `queue.PriorityQueue` usando a chave `-10 * rating + penaltyrec`. Para uma faixa entre as cinco execuções mais recentes, `penaltyrec = 5 - poshist`, com posição zero para a execução mais recente. Para as demais, a penalidade é zero. O ID desempata prioridades iguais. Assim, ratings altos saem primeiro e execuções recentes recebem uma pequena penalidade.

O estado salvo em JSON mantém a playlist e seu cursor, a fila, o histórico, o nome da playlist e a faixa atual. Para restaurar, carregue a biblioteca correspondente antes de executar `load estado.json`.

## Testes

Na pasta que contém `mediap`, execute:

```text
python -m unittest test_mediap -v
```

Para medir a cobertura, instale `coverage` opcionalmente e rode:

```text
python -m pip install coverage
python -m coverage run -m unittest test_mediap
python -m coverage report -m
```

Os testes verificam a lista e o cursor, a precedência da fila, o limite do histórico, a ordenação por prioridade e a persistência do estado, o teste atingiu uma coverage de aproximadamente 88%.

## Arquivos excluídos

Adicionado exceção para as pastas `pycache` ao arquivo .gitignore