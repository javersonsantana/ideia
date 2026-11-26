# Turma do Hello

App de inglês para crianças pequenas que **ainda não leem** (a partir de 4 anos), com três personagens
originais: **Bolt** (robô), **Luna** (gata astronauta) e **Tuco** (tucano).

Nada depende de leitura: o personagem fala as instruções em português e as palavras em inglês, e todos
os botões são desenhos. Cada lição ensina 6 palavras em cerca de 4 minutos:

1. apresenta 3 palavras (escutar, tocar na figura, repetir em voz alta);
2. pratica essas 3 ("Cadê? dog") com 2 e depois 3 figuras;
3. repete o mesmo com as outras 3 palavras;
4. termina misturando as 6, com 4 figuras por vez.

Quando a criança erra, o app diz o nome da figura tocada e pergunta de novo; depois de dois erros,
a figura certa pisca. No fim, a criança ganha de 1 a 3 estrelas.

Lições atuais: Animals, Colors, Numbers, Food, Toys, Body.

## Como rodar

Não tem build nem dependências. Sirva a pasta com qualquer servidor estático:

```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

## Som e microfone

- **Som:** todas as falas são gravações em `audio/` (voz sintética natural, geradas por `tools/make_audio.py`),
  então o som funciona em qualquer aparelho e sem internet.
- **Estrelinhas:** cada acerto (falar a palavra ou achar a figura) vale uma estrelinha, com festa na tela,
  sininho e parabéns falado. O total aparece na tela inicial.
- **Microfone:** na apresentação de cada palavra aparece um botão 🎤. A criança toca, repete a palavra e o app
  confere com o reconhecimento de voz do navegador: mostra ✅ se entendeu ou 🔁 para tentar de novo.
  Funciona no Chrome (computador ou Android), em página HTTPS ou `localhost`. O reconhecimento erra bastante
  com crianças pequenas, por isso nunca trava a lição: depois de duas tentativas dá para seguir sem a estrelinha.
- **Sem microfone:** o app avisa na primeira tela que não consegue ouvir e não finge que conferiu: a criança
  só repete em voz alta e segue, e as estrelinhas vêm de achar a figura certa.

## Instalar no Android

O app é um PWA (`manifest.json` + `sw.js`). Publicado em HTTPS (por exemplo, GitHub Pages),
o Chrome oferece "Adicionar à tela inicial" e ele passa a abrir em tela cheia e sem internet.

Para publicar na Play Store depois, o mesmo código pode ser empacotado com
[Bubblewrap/TWA](https://developer.chrome.com/docs/android/trusted-web-activity) ou Capacitor.

## Como adicionar uma lição

Tudo fica em `index.html`, na lista `UNITS`. Cada lição tem 6 `words` no formato `[inglês, figura]`
(a figura é um emoji, uma cor com `kind:'sw'` ou um número com `kind:'num'`) e um `pt` com o tema
falado em português ("os animais"). Prefira palavras concretas, que cabem em um desenho.
Depois acrescente as mesmas palavras em `tools/make_audio.py` e rode o script para gravar os áudios.

## Sobre os personagens

Os personagens são originais de propósito. Personagens famosos de filmes e desenhos são marcas
registradas: usá-los sem licença faz o app ser removido da Play Store e os vídeos derrubados no YouTube.
