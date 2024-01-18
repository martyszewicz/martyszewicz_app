let gameSocket;

document.addEventListener('DOMContentLoaded', () => {
    const infoDisplay = document.querySelector('#info');
    let roomName = 'default_room';
    let chatTextDom = 'default_chatText';
    let infoMessageDom = document.getElementById('defaultInfoMessage');
    let gameState = ["", "", "", "", "", "", "", "", ""]
    let element = document.querySelectorAll('.space')
    const user_username = JSON.parse(document.getElementById('user_username').textContent)
    let opponent = null;
    let playersTurn;
    let game_creator;
    let gameOver = false;

    function show_info(text) {
    // Show text in defaultInfoMessage div
        infoMessageDom.style.display = 'block';
        infoMessageDom.innerText = text;
    }

    function updatePlayers() {
        if (gameMode === 'multiPlayer') {
            if (user_username === game_creator){
                    playersTurn = true
                }
            document.getElementById('opponent').innerText = opponent ? 'X: ' + opponent : 'Czekam na przeciwnika';
        } else {
            document.getElementById('opponent').innerText = 'X: Komputer';
        }
    }

    if (gameMode !== 'singlePlayer') {
        roomName = JSON.parse(document.getElementById('room-name').textContent);
        const chatTextDom = document.querySelector('#chat-text');
        const infoMessageDom = document.querySelector('#info-message');
    }
    // Select Player Mode
    if (gameMode === 'singlePlayer') {
        startSinglePlayer();
    } else {
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

    // Multiplayer
    function startMultiPlayer() {

        //If user click on board
        element.forEach(function(elem){
            elem.addEventListener("click", function(event){
                console.log("tura przed ifem", playersTurn, gameOver)
                if (!gameOver){
                    if (playersTurn){
                        if (opponent){
                            setText(event.currentTarget.getAttribute('data-cell-index'), user_username);
                        }
                    } else {
                        show_info("It is not your turn")
                    }
                }
            });
        });

        //Put "X" or "O" on the board
        function setText(index, user_username){
            if(gameState[parseInt(index)] == ""){
                value = (user_username === opponent) ? 'X' : 'O';
                gameState[parseInt(index)] = value
                element[parseInt(index)].innerHTML = value
//                send info about players choice
                gameSocket.send(JSON.stringify({
                    'type': 'players_choice',
                    'player': user_username,
                    'index': index,
                    'value': value
                }))
                playersTurn = false
                show_info ("")
                console.log("tura po postawieniu znaku", playersTurn)
                checkWon(user_username, value)
            }else{
                show_info ("You can not fill this place")
                setTimeout(function() {
                    infoMessageDom.innerText = " ";
                    }, 1000);
                }
        }

        // check for draw
        function checkGameEnd(){
            var count = 0;
            gameState.map((game)=>{
                if(game != ""){
                    count ++;
                }
            })

            if (count >= 9){
                gameSocket.send(JSON.stringify({
                    'type': 'game_end',
                    'player': "draw",
                }))
            }
        }

        // check for winner
        function checkWon (player, value){
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
                gameSocket.send(JSON.stringify({
                    'type': 'game_end',
                    'player': user_username,
                }))
            }

            checkGameEnd();
        }

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

            console.log('Received data:', data);

            switch (data.type) {
                case 'chat_message':
                    document.querySelector('#chat-text').value += (data.username + ': ' + data.message + '\n');
                    chatTextDom.scrollTop = chatTextDom.scrollHeight;
                    break;
                case 'players_choice':
                    console.log(data)
                    setTextFromOpponent(data.index, data.player, data.value)
                    if (data.player !== user_username) {
                        playersTurn = true;
                        show_info ("Your turn");
                    }
                    break;
                case "game_end":
                    if (data.player === "draw"){
                        show_info("Draw");
                    } else {
                        show_info(data.player + " win the game");
                    }
                    gameOver = true;
                    break;
                case 'system_message':
                    console.log("system message", data.type)
                    show_info(data.message);
                    break;
                case 'update_players':
                    opponent = data.opponent;
                    game_creator = data.game_creator;
                    updatePlayers();
                    console.log("gamecreator, opponent from case updateplayers and playersturn", game_creator, opponent, playersTurn)
                    console.log("username", user_username)
                    break;
                default:
                    console.log('Unknown message type:', data.type);
                    break;
            }
        };
  }
})