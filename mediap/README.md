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

Os testes verificam a lista e o cursor, a precedência da fila, o limite do histórico, a ordenação por prioridade e a persistência do estado.

## Arquivos excluídos

Adicionado exceção para as pastas `pycache` ao arquivo .gitignore

## Roteiro manual completo

1. Na pasta que contém `mediap`, inicie com `python -m mediap.main`.
2. Rode `help` e `library load mediap/library.json`. Confira a mensagem com 10 faixas.
3. Rode `library list`, depois `library list --by rating`, `library list --by title` e `library list --by artist`. Cada forma deve listar as faixas na ordem indicada.
4. Rode `playlist new teste`, `playlist add 3`, `playlist add 7` e `playlist add 1`. Use `playlist show` para conferir a ordem e o cursor na primeira faixa.
5. Rode `play`, `next` e `prev`. A linha iniciada por `>>> Tocando:` deve indicar a faixa executada. Rode `prev` na primeira faixa e `next` até a última para conferir as mensagens de limite.
6. Rode `enqueue 5`, `enqueue 8` e `queue show`. Rode `next` duas vezes: as duas faixas enfileiradas tocam primeiro. `playlist show` confirma que o cursor da playlist não avançou nesses dois comandos.
7. Rode `history` e confira que a execução mais recente aparece primeiro.
8. Rode `smart-shuffle 5` e `playlist show`. O resultado terá cinco faixas, com rating alto em primeiro lugar; faixas tocadas recentemente recebem a penalidade descrita acima. Teste também `smart-shuffle 11` para conferir a validação do limite.
9. Rode `enqueue 5`, `play` e `next` para preencher estado variado. Salve com `save estado.json`. Anote a saída de `playlist show`, `queue show` e `history`.
10. Rode `playlist new temporaria`, `playlist add 4` e então `load estado.json`. As saídas de `playlist show`, `queue show` e `history` devem voltar ao estado anotado. Encerre com `quit`.

O descarte FIFO do histórico ao ultrapassar 20 itens e a igualdade de estado após salvar e restaurar também são verificados nos testes automatizados.
