let gameSocket;
let chatTextDom;

document.addEventListener('DOMContentLoaded', () => {
    const infoDisplay = document.querySelector('#info');
    let roomName = 'default_room';
    let infoMessageDom = document.getElementById('defaultInfoMessage');
    let gameState = ["", "", "", "", "", "", "", "", ""]
    let element = document.querySelectorAll('.space')
    let opponent = null;
    let playersTurn;
    let game_creator;
    let gameOver = false;
    let user_username;

    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function setText(index, user_username) {
        if (!gameOver){
            if (gameState[parseInt(index)] === "") {
                var value;
                if (gameMode === 'singlePlayer') {
                    value = 'O';
                } else if (gameMode === 'multiPlayer') {
                    value = (user_username === opponent) ? 'X' : 'O';
                    // send info about player's choice
                    gameSocket.send(JSON.stringify({
                        'type': 'players_choice',
                        'player': user_username,
                        'index': index,
                        'value': value
                    }));
                }

                gameState[parseInt(index)] = value;
                element[parseInt(index)].innerHTML = value;

                playersTurn = !playersTurn;
                show_info("");
                checkWon(user_username, value)

                if (!gameOver && gameMode === 'singlePlayer' && !playersTurn) {
                    show_info(translations.computerThinks, true);
                    setTimeout(function () {
                        infoMessageDom.innerText = '';
                        spinner.style.display = 'none';
                        computerMove();
                        checkWon("Computer", "X");
                    }, 1000);
                }
            } else {
                show_info(translations.thisPlaceIsNotEmpty);
                setTimeout(function () {
                    infoMessageDom.innerText = "";
                }, 1000);
            }
        }
    }

    function computerMove() {
        var randomNum;
        do {
            randomNum = getRandomInt(0, 8);
        } while (gameState[randomNum] !== "");

        gameState[randomNum] = "X";
        element[randomNum].innerHTML = "X";
        playersTurn = true;
    }

    function checkWon(player, value) {
        var win = false;
        var winConditions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ];

        for (var i = 0; i < winConditions.length; i++) {
            var condition = winConditions[i];
            if (gameState[condition[0]] === value && gameState[condition[1]] === value && gameState[condition[2]] === value) {
                win = true;
                break;
            }
        }

        if (win) {
            if (gameMode === 'multiPlayer') {
                gameSocket.send(JSON.stringify({
                    'type': 'game_end',
                    'player': user_username,
                }));
            } else if (gameMode === 'singlePlayer') {
                if (value === "O") {
                    show_info(translations.youWin);
                } else {
                    show_info(translations.computerWin);
                }
                gameOver = true;
            }
        }

        if (!win) {
            checkGameEnd();
        }
    }

    function checkGameEnd() {
        var count = 0;
        gameState.forEach((game) => {
            if (game !== "") {
                count++;
            }
        });

        if (count >= 9) {
            if (gameMode === 'multiPlayer') {
                gameSocket.send(JSON.stringify({
                    'type': 'game_end',
                    'player': "draw",
                }));
            } else if (gameMode === 'singlePlayer') {
                show_info(translations.draw);
                gameOver = true;
            }
        }
    }


    function show_info(text, showSpinner) {
    // Show text in defaultInfoMessage div
        infoMessageDom.style.display = 'block';
        infoMessageDom.innerText = text;
        if (showSpinner) {
            spinner.style.display = 'inline-block'
        }
    }

    function updatePlayers() {
        if (gameMode === 'multiPlayer') {
            const user_username = JSON.parse(document.getElementById('user_username').textContent)
            if (user_username === game_creator){
                    playersTurn = true
                }
            document.getElementById('opponent').innerText = opponent ? 'X: ' + opponent : translations.waitForOpponent;
        }
    }

    if (gameMode !== 'singlePlayer') {
        roomName = JSON.parse(document.getElementById('room-name').textContent);
        chatTextDom = document.querySelector('#chat-text');
    }
    // Select Player Mode
    if (gameMode === 'singlePlayer') {
        user_username = "user";
        opponent = "computer";
        var spinner = document.getElementById('spinner');
        startSinglePlayer();
    } else {
        user_username = JSON.parse(document.getElementById('user_username').innerHTML);
        // create websocket
        const languagePath = window.location.pathname.split('/')[1];
        gameSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/' + languagePath +
            '/ws/tictactoe/multi_player/' +
            roomName +
            '/'
        );
        startMultiPlayer();
    }
    // Singleplayer
    function startSinglePlayer() {
        playersTurn = true
        //If user click on board
        element.forEach(function(elem){
            elem.addEventListener("click", function(event){
                if (!gameOver){
                    if (playersTurn){
                        setText(event.currentTarget.getAttribute('data-cell-index'), user_username);
                    } else {
                        show_info(translations.notYourTurn)
                    }
                }
            });
        });
    }

    // Multiplayer
    function startMultiPlayer() {
        //If user click on board
        element.forEach(function(elem){
            elem.addEventListener("click", function(event){
                if (!gameOver){
                    if (playersTurn){
                        if (opponent){
                            setText(event.currentTarget.getAttribute('data-cell-index'), user_username);
                        }
                    } else {
                        show_info(translations.notYourTurn)
                    }
                }
            });
        });

        // Chat messages functions
        function sendMessage() {
            const messageInputDom = document.querySelector('#input');
            const message = messageInputDom.value.trim();
            if (message !== '') {
                gameSocket.send(JSON.stringify({
                    'type': 'chat_message',
                    'message': message,
                    'username': user_username,
                }));
                messageInputDom.value = '';
            }
        }

        document.querySelector('#chat-form').onsubmit = function (e) {
            e.preventDefault();
            sendMessage();
        };

        document.querySelector('#submit').onclick = function (e) {
            sendMessage();
        };
//      Insert X or O on board from opponent move
        function setTextFromOpponent(index, player, value){
            gameState[parseInt(index)] = value
            element[parseInt(index)].innerHTML = value
        }

//        Recieve messages
        gameSocket.onmessage = function (event) {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'chat_message':
                    document.querySelector('#chat-text').value += (data.username + ': ' + data.message + '\n');
                    chatTextDom.scrollTop = chatTextDom.scrollHeight;
                    break;
                case 'players_choice':
                    setTextFromOpponent(data.index, data.player, data.value)
                    if (data.player !== user_username) {
                        playersTurn = true;
                        show_info (translations.yourTurn);
                    }
                    break;
                case "game_end":
                    if (data.player === "draw"){
                        show_info(translations.draw);
                    } else {
                        show_info(data.player + " " + translations.playerWin);
                    }
                    gameOver = true;
                    break;
                case 'system_message':
                    const messageParts = data.message.split(' ');
                    const username = messageParts[0];
                    console.log(username, messageParts)
                    if (messageParts.length === 2 && messageParts[1] === 'join') {
                        show_info(`${username} ${translations.join}`);
                    } else if (messageParts.length === 2 && messageParts[1] === 'left') {
                        show_info(`${username} ${translations.left}`);
                    } else {
                        show_info(data.message);
                    }
                    console.log(translations.join, translations.left)
                    break;
                case 'update_players':
                    opponent = data.opponent;
                    game_creator = data.game_creator;
                    updatePlayers();
                    break;
                default:
                    console.log('Unknown message type:', data.type);
                    break;
            }
        };
  }
})