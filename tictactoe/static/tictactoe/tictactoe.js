let gameSocket;

document.addEventListener('DOMContentLoaded', () => {
    const infoDisplay = document.querySelector('#info');
    let user_username = 'default_username';
    let roomName = 'default_room';
    let chatTextDom = 'default_chatText';
    let infoMessageDom = 'defaultInfoMessage';
    let gameState = ["", "", "", "", "", "", "", "", ""]
    let element = document.querySelectorAll('.space')
    let opponent = null;

    function updatePlayers() {
        if (gameMode === 'multiPlayer') {
            document.getElementById('opponent').innerText = opponent ? 'X: ' + opponent : 'Czekam na przeciwnika';
        } else {
            document.getElementById('opponent').innerText = 'X: Komputer';
        }
    }

    if (gameMode !== 'singlePlayer') {
        user_username = JSON.parse(document.getElementById('user_username').textContent);
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

        //Put "X" or "O" on the board
        element.forEach(function(elem){
            elem.addEventListener("click", function(event){
                setText(event.currentTarget.getAttribute('data-cell-index'), user_username)
            })
        })


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
            }else{
                infoMessageDom = document.getElementById('defaultInfoMessage');
                infoMessageDom.style.display = 'block';
                infoMessageDom.innerText = "You can not fill this place";
                setTimeout(function() {
                    infoMessageDom.innerText = " ";
                    }, 1000);
                }
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
                case 'system_message':
                    console.log("system message", data.type)
                    infoMessageDom = document.getElementById('defaultInfoMessage');
                    infoMessageDom.style.display = 'block';
                    infoMessageDom.innerText = data.message;
                    break;
                case 'update_players':
                    opponent = data.opponent;
                    updatePlayers();
                    break;
                default:
                    console.log('Unknown message type:', data.type);
                    break;
            }
        };
  }
})