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

Lições atuais: Animals, Colors, Numbers, Food, Toys, Body (palavras) e duas lições de frases do dia a dia:
Hello! ("Hello, my friend!", "I love you!", "Good night!"...) e I love... ("I have a dog.", "My car is blue.",
"I love my grandma."...). Nas frases, o personagem fala em inglês e depois diz o que quer dizer em português.

## Como rodar

Não tem build nem dependências. Sirva a pasta com qualquer servidor estático:

```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

## Som e microfone

- **Som:** todas as falas são gravações em `audio/` (voz sintética natural, geradas por `tools/make_audio.py`),
  então o som funciona em qualquer aparelho e sem internet.
- **Voz do aparelho (opcional):** em "Para os pais", na tela inicial, dá para trocar a voz gravada das palavras
  em inglês pela voz do próprio aparelho, para comparar qual soa melhor.
- **Estrelinhas:** cada acerto (falar a palavra ou achar a figura) vale uma estrelinha, com festa na tela,
  sininho e parabéns falado. O total aparece na tela inicial.
- **Progresso guardado:** o app guarda no aparelho o total de estrelinhas, a nota de cada lição, os dias de
  estudo e, para cada palavra, quantas vezes a criança achou a figura, falou certo e errou. O botão ⭐🏆 da
  tela inicial abre o álbum: todas as palavras com 0 a 3 estrelas (achar a figura vale 1 ponto, falar certo
  vale 2; com 1, 3 e 6 pontos a palavra chega a 1, 2 e 3 estrelas). Lá também há um resumo para os pais,
  com as palavras que precisam de mais treino, e o botão para apagar o progresso.
- **Microfone:** na apresentação de cada palavra aparece um botão 🎤. A criança aperta, segura, fala e solta, e o app
  confere com o reconhecimento de voz do navegador: mostra ✅ se entendeu ou 🔁 para tentar de novo.
  Funciona no Chrome (computador ou Android), em página HTTPS ou `localhost`. A criança só avança quando
  acerta; como o reconhecimento pode errar com crianças pequenas, depois de 5 tentativas aparece um link
  pequeno para o adulto pular a palavra, sem estrelinha.
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
Uma lição de frases usa `kind:'ph'` e cada item é `[inglês, figura, nome do áudio, palavras que o microfone
precisa ouvir, tradução]`; a frase e a tradução também entram em `PHRASES` no script de áudio.
Depois acrescente as mesmas palavras em `tools/make_audio.py` e rode o script para gravar os áudios.

## Sobre os personagens

Os personagens são originais de propósito. Personagens famosos de filmes e desenhos são marcas
registradas: usá-los sem licença faz o app ser removido da Play Store e os vídeos derrubados no YouTube.
