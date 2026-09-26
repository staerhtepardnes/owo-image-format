# Especificação do formato OWO1

## Visão geral

Um arquivo OWO é um arquivo binário little-endian composto por um cabeçalho de
16 bytes seguido pelo payload de pixels. A versão atual suporta imagens RGB e
RGBA, sem perdas.

## Cabeçalho

| Offset | Tamanho | Tipo | Campo |
|---:|---:|---|---|
| 0 | 4 | bytes | **magic**: exatamente `OWO1` |
| 4 | 4 | uint32 | **width**: largura em pixels |
| 8 | 4 | uint32 | **height**: altura em pixels |
| 12 | 1 | uint8 | **channels**: `3` para RGB ou `4` para RGBA |
| 13 | 1 | uint8 | **compression**: `0` = raw, `1` = RLE |
| 14 | 2 | uint16 | **reserved**: deve ser zero; reservado para extensões futuras |

Todos os inteiros usam little-endian. Largura e altura devem ser maiores que
zero. A ordem dos pixels é row-major, da esquerda para a direita e de cima
para baixo. Cada componente é um byte (8 bits), na ordem R, G, B e, quando
presente, A.

## Payload raw (`compression = 0`)

O payload contém exatamente `width × height × channels` bytes de pixels, sem
metadados adicionais.

## Payload RLE (`compression = 1`)

O payload é uma sequência de pacotes. Cada pacote contém:

1. `run_length`: uint32 little-endian, maior que zero;
2. `pixel`: exatamente `channels` bytes.

O pixel deve ser repetido `run_length` vezes na sequência row-major. A soma dos
run lengths deve ser exatamente `width × height`. Runs não atravessam nenhuma
fronteira especial: a imagem é tratada como uma sequência linear de pixels.

## Compatibilidade e validação

Leitores devem rejeitar magic, dimensões, número de canais, método de
compressão ou tamanhos de payload inválidos. Bytes reservados diferentes de
zero indicam flags/extensões que um leitor desta versão não entende.
