# Turma do Hello

App de inglês bem básico (nível pré-A1/A1) para crianças, com três personagens originais:
**Bolt** (robô), **Luna** (gata astronauta) e **Tuco** (tucano).

Cada lição tem três atividades:

- **Aprender** – cartas com figura, palavra, tradução e áudio.
- **Conversar** – o personagem fala em inglês e a criança escolhe a resposta.
- **Jogar** – escutar a palavra e tocar na figura certa; vale até 3 estrelas.

Lições atuais: Hello!, Colors, Numbers, Animals, Food, Family.

## Como rodar

Não tem build nem dependências. Sirva a pasta com qualquer servidor estático:

```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

O áudio usa a voz em inglês do próprio aparelho (Web Speech API). No Android, funciona melhor no Chrome.

## Instalar no Android

O app é um PWA (`manifest.json` + `sw.js`). Publicado em HTTPS (por exemplo, GitHub Pages),
o Chrome oferece "Adicionar à tela inicial" e ele passa a abrir em tela cheia e sem internet.

Para publicar na Play Store depois, o mesmo código pode ser empacotado com
[Bubblewrap/TWA](https://developer.chrome.com/docs/android/trusted-web-activity) ou Capacitor.

## Como adicionar uma lição

Tudo fica em `index.html`, na lista `UNITS`. Cada lição é um objeto com:

- `words`: `[inglês, português, figura]` – a figura é um emoji (ou uma cor com `kind:'sw'`, ou um número com `kind:'num'`);
- `talk`: falas do personagem com `en`, `pt` e `opts` (a **primeira** opção é a resposta certa; a ordem é embaralhada na tela).

## Sobre os personagens

Os personagens são originais de propósito. Personagens famosos de filmes e desenhos são marcas
registradas: usá-los sem licença faz o app ser removido da Play Store e os vídeos derrubados no YouTube.
