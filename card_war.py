import random
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Game Logic & Data ---
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {r: i for i, r in enumerate(ranks, start=2)}

def create_deck():
    return [{'rank': r, 'suit': s, 'value': values[r]} for s in suits for r in ranks]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_decks')
def get_decks():
    count_per_player = request.args.get('count', default=26, type=int)
    debug_mode = request.args.get('debug', default=False, type=bool)
    total_needed = count_per_player * 2

    if debug_mode:
        # Debug mode: Only cards 2-4 with two copies each (for very frequent tie testing)
        deck = []
        for suit in suits:
            for rank in ['2', '3', '4']:
                # Two copies of each card
                deck.append({'rank': rank, 'suit': suit, 'value': values[rank]})
                deck.append({'rank': rank, 'suit': suit, 'value': values[rank]})
        random.shuffle(deck)
        deck = deck[:total_needed]
    else:
        deck = create_deck()
        random.shuffle(deck)
        deck = deck[:total_needed]
    
    half = len(deck) // 2
    p1_deck = deck[:half]
    p2_deck = deck[half:]
    
    return jsonify({'p1': p1_deck, 'p2': p2_deck})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEON WAR</title>
    <style>
        body {
            margin: 0;
            background-color: #020408;
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace;
            color: #00f3ff;
            user-select: none;
        }
        canvas { display: block; }
        
        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none; 
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .hud {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 80px;
            padding: 20px;
            padding-right: 120px; 
            font-size: 20px;
            font-weight: bold;
            text-transform: uppercase;
            z-index: 10;
        }

        .team-stats {
            text-align: center;
        }

        #computer-icon {
            font-size: 40px;
            text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
            transition: color 0.3s, text-shadow 0.3s;
        }

        .controls {
            text-align: center;
            padding-bottom: 20px;
            font-size: 18px;
            color: rgba(0, 243, 255, 0.7);
            background: rgba(0, 10, 20, 0.8);
            padding: 10px;
            border-top: 1px solid #00f3ff;
            box-shadow: 0 -5px 15px rgba(0, 243, 255, 0.2);
        }

        .key {
            display: inline-block;
            background: #00111a;
            color: #00f3ff;
            border: 1px solid #00f3ff;
            padding: 2px 8px;
            border-radius: 2px;
            margin: 0 5px;
            box-shadow: 0 0 5px #00f3ff;
        }
        
        #message {
            position: absolute;
            top: 15%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 48px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0 0 10px #ff5500, 0 0 20px #ff5500;
            display: none;
            white-space: nowrap;
            pointer-events: none;
            letter-spacing: 5px;
        }

        #start-menu {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(2, 4, 8, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            transition: opacity 0.5s ease-out;
        }

        #start-menu.hidden {
            opacity: 0;
            pointer-events: none;
        }

        .menu-title {
            font-size: 72px;
            font-weight: bold;
            color: #00f3ff;
            text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            letter-spacing: 10px;
            margin-bottom: 60px;
            font-family: 'Courier New', Courier, monospace;
        }

        .player-inputs {
            display: flex;
            gap: 100px;
            margin-bottom: 60px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .input-label {
            font-size: 18px;
            color: #00f3ff;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        .input-group:nth-child(2) .input-label {
            color: #ff5500;
        }

        .player-name-input {
            background: rgba(0, 17, 26, 0.8);
            border: 2px solid #00f3ff;
            color: #00f3ff;
            padding: 15px 20px;
            font-size: 20px;
            font-family: 'Courier New', Courier, monospace;
            text-align: center;
            width: 250px;
            outline: none;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
            transition: all 0.3s ease;
        }

        .player-name-input:focus {
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
        }

        .input-group:nth-child(2) .player-name-input {
            border-color: #ff5500;
            color: #ff5500;
            box-shadow: 0 0 10px rgba(255, 85, 0, 0.3);
        }

        .input-group:nth-child(2) .player-name-input:focus {
            box-shadow: 0 0 20px rgba(255, 85, 0, 0.6);
        }

        #initialize-btn {
            background: transparent;
            border: 3px solid #00f3ff;
            color: #00f3ff;
            padding: 20px 60px;
            font-size: 32px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            text-transform: uppercase;
            letter-spacing: 8px;
            cursor: pointer;
            text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.4), inset 0 0 20px rgba(0, 243, 255, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        #initialize-btn:hover {
            background: rgba(0, 243, 255, 0.1);
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.6), inset 0 0 30px rgba(0, 243, 255, 0.2);
        }

        #initialize-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }

        #initialize-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 243, 255, 0.4), transparent);
            animation: scan 2s infinite;
        }

        @keyframes scan {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        #debug-btn {
            position: absolute;
            bottom: 30px;
            right: 30px;
            pointer-events: auto;
            background-color: rgba(0,0,0,0.5);
            border: 1px solid #ff5500;
            color: #ff5500;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 0 5px #ff5500;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #debug-btn:hover {
            background-color: #ff5500;
            color: #000;
        }
    </style>
</head>
<body>

    <canvas id="gameCanvas"></canvas>
    <button id="debug-btn">?</button>

    <div id="start-menu">
        <div class="menu-title">NEON WAR</div>
        <div class="player-inputs">
            <div class="input-group">
                <label class="input-label">Player 1</label>
                <input type="text" id="p1-name" class="player-name-input" value="DRIFTERS" maxlength="15">
            </div>
            <div class="input-group">
                <label class="input-label">Player 2</label>
                <input type="text" id="p2-name" class="player-name-input" value="SCAVS" maxlength="15">
            </div>
        </div>
        <button id="initialize-btn">INITIALIZE</button>
    </div>

    <div id="ui-layer">
        <div class="hud">
            <div class="team-stats">
                <div id="p1-stats" style="color: #00f3ff; text-shadow: 0 0 8px #00f3ff;">DRIFTERS<br>Buffer: 26 | Recurrable: 0</div>
            </div>
            <div id="computer-icon">🖥️</div>
            <div class="team-stats">
                <div id="p2-stats" style="color: #ff5500; text-shadow: 0 0 8px #ff5500;">SCAVS<br>Buffer: 26 | Recurrable: 0</div>
            </div>
        </div>
        <div id="message">SYSTEM CRITICAL</div>
        <div class="controls">
            <span id="p1-controls-name">DRIFTERS</span>: Press <span class="key">Z</span> &nbsp;|&nbsp; <span id="p2-controls-name">SCAVS</span>: Press <span class="key">M</span>
        </div>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const p1StatsEl = document.getElementById('p1-stats');
const p2StatsEl = document.getElementById('p2-stats');
const messageEl = document.getElementById('message');
const computerIconEl = document.getElementById('computer-icon');
const debugBtn = document.getElementById('debug-btn');
const startMenu = document.getElementById('start-menu');
const initializeBtn = document.getElementById('initialize-btn');
const p1NameInput = document.getElementById('p1-name');
const p2NameInput = document.getElementById('p2-name');
const p1ControlsNameEl = document.getElementById('p1-controls-name');
const p2ControlsNameEl = document.getElementById('p2-controls-name');

let p1Name = 'DRIFTERS';
let p2Name = 'SCAVS';
let gameInitialized = false;

let WIDTH, HEIGHT;

let p1Deck = [];
let p2Deck = [];
let p1Discard = [];
let p2Discard = [];

let p1CardActive = null; 
let p2CardActive = null;

let particles = []; 
let gameState = 'WAITING'; 
let circuitryOffset = 0;

let warCards = []; 
let isWar = false;
let activeWarCards = []; 

const CARD_W = 120;
const CARD_H = 170;
const COLORS = {
    p1: '#00f3ff',
    p2: '#ff5500',
    bg: '#020408',
    grid: 'rgba(0, 243, 255, 0.1)',
    circuit: 'rgba(0, 243, 255, 0.4)'
};

let screenScale = 1;

let tableJunk = [];

function generateJunk() {
    tableJunk = [];
    const centerX = WIDTH / 2;
    const centerY = HEIGHT / 2;
    const range = 300;
    
    for(let i=0; i<15; i++) {
        tableJunk.push({
            x: centerX + (Math.random() - 0.5) * range,
            y: centerY + (Math.random() - 0.5) * range * 0.6,
            w: 20 + Math.random() * 40,
            h: 10 + Math.random() * 20,
            type: Math.random() > 0.5 ? 'rect' : 'chip',
            rot: Math.random() * Math.PI * 2,
            color: Math.random() > 0.5 ? '#111' : '#222'
        });
    }
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 8 + 2;
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;
        this.alpha = 1;
        this.color = color;
        this.decay = Math.random() * 0.04 + 0.01;
        this.shape = Math.random() > 0.5 ? 'rect' : 'line';
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.alpha -= this.decay;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.fillStyle = this.color;
        ctx.strokeStyle = this.color;
        
        if (this.shape === 'rect') {
            ctx.fillRect(this.x, this.y, 4, 4);
        } else {
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x + this.vx*3, this.y + this.vy*3);
            ctx.stroke();
        }
        ctx.restore();
    }
}

class ActiveCard {
    constructor(cardObj, owner, startX, startY) {
        this.data = cardObj;
        this.owner = owner; 
        this.x = startX;
        this.y = startY;
        this.targetX = startX;
        this.targetY = startY;
        this.faceUp = false;
        this.wobble = 0;
        this.scale = 1;
        this.opacity = 0;
        this.state = 'ENTERING'; 
        this.mainColor = owner === 1 ? COLORS.p1 : COLORS.p2;
    }

    update() {
        this.x += (this.targetX - this.x) * 0.1;
        this.y += (this.targetY - this.y) * 0.1;
        
        if (this.state === 'ENTERING') {
            this.opacity += 0.1;
            if (this.opacity > 1) this.opacity = 1;
        } else if (this.state === 'ACTIVE') {
            if (this.opacity < 1) this.opacity = 1;
        }

        if (this.state === 'CLASHING') {
            this.wobble = Math.random() * 4 - 2;
        } else {
            this.wobble = 0;
        }
        
        if (this.state === 'FADING') {
            this.opacity -= 0.05;
            this.scale += 0.05;
        }
        
        if (this.state === 'RESOLVED') {
            this.opacity -= 0.01;
            if (this.opacity < 0.3) this.opacity = 0.3;
        }
    }

    draw(ctx) {
        if (this.opacity <= 0) return;

        ctx.save();
        ctx.translate(this.x + this.wobble, this.y);
        ctx.scale(this.scale, this.scale);
        ctx.globalAlpha = this.opacity;

        ctx.fillStyle = 'rgba(2, 4, 8, 0.8)';
        ctx.strokeStyle = this.mainColor;
        ctx.lineWidth = 3;
        ctx.shadowColor = this.mainColor;
        ctx.shadowBlur = 10;
        
        ctx.beginPath();
        ctx.roundRect(-CARD_W/2, -CARD_H/2, CARD_W, CARD_H, 4);
        ctx.fill();
        ctx.stroke();

        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(255,255,255,0.2)';
        ctx.strokeRect(-CARD_W/2 + 5, -CARD_H/2 + 5, CARD_W - 10, CARD_H - 10);

        if (this.faceUp) {
            ctx.fillStyle = this.mainColor;
            ctx.font = 'bold 40px "Courier New", monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            const rankOpacity = Math.min(this.opacity * 2, 1.0);
            ctx.save();
            ctx.globalAlpha = rankOpacity;
            ctx.textAlign = 'left';
            ctx.fillText(this.data.rank, -CARD_W/2 + 15, -CARD_H/2 + 35);
            ctx.font = '30px "Courier New", monospace';
            ctx.fillText(this.data.suit, -CARD_W/2 + 15, -CARD_H/2 + 65);
            ctx.restore();

            ctx.font = '60px "Courier New", monospace';
            ctx.textAlign = 'center';
            ctx.shadowBlur = 20;
            ctx.fillText(this.data.suit, 0, 0);
            ctx.shadowBlur = 0;

            ctx.save();
            ctx.rotate(Math.PI);
            ctx.textAlign = 'left';
            ctx.font = 'bold 40px "Courier New", monospace';
            ctx.fillText(this.data.rank, -CARD_W/2 + 15, -CARD_H/2 + 35);
            ctx.font = '30px "Courier New", monospace';
            ctx.fillText(this.data.suit, -CARD_W/2 + 15, -CARD_H/2 + 65);
            ctx.restore();

        } else {
            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(-CARD_W/2 + 10, -CARD_H/2 + 10, CARD_W - 20, CARD_H - 20);
            
            ctx.fillStyle = this.mainColor;
            ctx.globalAlpha = 0.5;
            ctx.font = '20px "Courier New"';
            ctx.textAlign = 'center';
            ctx.fillText("ENCRYPTED", 0, -20);
            
            ctx.beginPath();
            ctx.moveTo(-CARD_W/2, -CARD_H/4);
            ctx.lineTo(CARD_W/2, -CARD_H/4);
            ctx.moveTo(-CARD_W/2, CARD_H/4);
            ctx.lineTo(CARD_W/2, CARD_H/4);
            ctx.stroke();
        }

        ctx.restore();
    }
}

function resize() {
    WIDTH = canvas.width = window.innerWidth;
    HEIGHT = canvas.height = window.innerHeight;
    
    const baseWidth = 1920;
    const baseHeight = 1080;
    screenScale = Math.min(WIDTH / baseWidth, HEIGHT / baseHeight, 1.2);
    
    console.log(`Resized to ${WIDTH}x${HEIGHT}, scale factor: ${screenScale.toFixed(3)}`);
    
    if (p1CardActive) {
        p1CardActive.targetX = WIDTH / 2;
        p1CardActive.targetY = HEIGHT / 2 - 20 * screenScale;
        console.log(`Repositioned P1 active card to (${p1CardActive.targetX.toFixed(0)}, ${p1CardActive.targetY.toFixed(0)})`);
    }
    if (p2CardActive) {
        p2CardActive.targetX = WIDTH / 2;
        p2CardActive.targetY = HEIGHT / 2 + 20 * screenScale;
        console.log(`Repositioned P2 active card to (${p2CardActive.targetX.toFixed(0)}, ${p2CardActive.targetY.toFixed(0)})`);
    }
    
    if (activeWarCards.length > 0) {
        const p1WarCards = activeWarCards.filter(c => c.owner === 1);
        const p2WarCards = activeWarCards.filter(c => c.owner === 2);
        
        for (let i = 0; i < p1WarCards.length; i++) {
            const card = p1WarCards[i];
            card.targetX = WIDTH / 2 - 150 * screenScale - 45 * screenScale * (p1WarCards.length - 1 - i);
            card.targetY = HEIGHT / 2 - 80 * screenScale - 35 * screenScale * (p1WarCards.length - 1 - i);
            card.x = card.targetX;
            card.y = card.targetY;
        }
        
        for (let i = 0; i < p2WarCards.length; i++) {
            const card = p2WarCards[i];
            card.targetX = WIDTH / 2 + 150 * screenScale + 45 * screenScale * (p2WarCards.length - 1 - i);
            card.targetY = HEIGHT / 2 + 80 * screenScale + 35 * screenScale * (p2WarCards.length - 1 - i);
            card.x = card.targetX;
            card.y = card.targetY;
        }
    }
    
    generateJunk();
}

async function initGame(countPerPlayer = 26) {
    resize();
    const response = await fetch(`/get_decks?count=${countPerPlayer}`);
    const data = await response.json();
    p1Deck = data.p1;
    p2Deck = data.p2;
    p1Discard = [];
    p2Discard = [];
    p1CardActive = null;
    p2CardActive = null;
    activeWarCards = [];
    warCards = [];
    gameState = 'WAITING';
    updateStats();
}

async function initGameDebug(countPerPlayer = 5) {
    resize();
    const response = await fetch(`/get_decks?count=${countPerPlayer}&debug=true`);
    const data = await response.json();
    p1Deck = data.p1;
    p2Deck = data.p2;
    p1Discard = [];
    p2Discard = [];
    p1CardActive = null;
    p2CardActive = null;
    activeWarCards = [];
    warCards = [];
    gameState = 'WAITING';
    updateStats();
    
    showMessage("DEBUG MODE: CARDS 2-4", '#ffff00');
    setTimeout(() => { messageEl.style.display = 'none'; }, 1500);
}

function updateStats() {
    p1StatsEl.innerHTML = `${p1Name}<br>Buffer: ${p1Deck.length} | Recurrable: ${p1Discard.length}`;
    p2StatsEl.innerHTML = `${p2Name}<br>Buffer: ${p2Deck.length} | Recurrable: ${p2Discard.length}`;
    
    const p1Total = p1Deck.length + p1Discard.length;
    const p2Total = p2Deck.length + p2Discard.length;
    
    if (p1Total > p2Total) {
        computerIconEl.style.color = COLORS.p1;
        computerIconEl.style.textShadow = `0 0 10px ${COLORS.p1}, 0 0 20px ${COLORS.p1}`;
    } else if (p2Total > p1Total) {
        computerIconEl.style.color = COLORS.p2;
        computerIconEl.style.textShadow = `0 0 10px ${COLORS.p2}, 0 0 20px ${COLORS.p2}`;
    } else {
        computerIconEl.style.color = '#ffffff';
        computerIconEl.style.textShadow = `0 0 10px #ffffff, 0 0 20px #ffffff`;
    }
}

function showMessage(msg, color='#ffffff') {
    messageEl.innerText = msg;
    messageEl.style.display = 'block';
    messageEl.style.color = color;
    messageEl.style.textShadow = `0 0 10px ${color}, 0 0 20px ${color}`;
}

function endGame(msg) {
    gameState = 'GAME_OVER';
    showMessage(msg, '#ff0000');
}

function playCard(player) {
    if (gameState === 'GAME_OVER') return;

    if (p1CardActive && p1CardActive.state === 'RESOLVED') {
        p1CardActive = null;
    }
    if (p2CardActive && p2CardActive.state === 'RESOLVED') {
        p2CardActive = null;
    }
    if (activeWarCards.length > 0) {
        activeWarCards = [];
    }

    if (player === 1) {
        if (p1CardActive) return; 

        if (p1Deck.length === 0) {
            if (p1Discard.length === 0) {
                endGame(`${p2Name} DOMINATE. ${p1Name} ELIMINATED.`);
                return;
            }
            p1Deck = shuffleArray([...p1Discard]);
            p1Discard = [];
            updateStats();
            showMessage(`${p1Name} RECYCLING...`, COLORS.p1);
            setTimeout(() => { messageEl.style.display = 'none'; }, 800);
        }

        const cardData = p1Deck.shift();
        p1CardActive = new ActiveCard(cardData, 1, 150 * screenScale, HEIGHT + 100);
        setTimeout(() => { p1CardActive.faceUp = true; }, 100);
        updateStats();

    } else {
        if (p2CardActive) return;

        if (p2Deck.length === 0) {
            if (p2Discard.length === 0) {
                endGame(`${p1Name} DOMINATE. ${p2Name} ELIMINATED.`);
                return;
            }
            p2Deck = shuffleArray([...p2Discard]);
            p2Discard = [];
            updateStats();
            showMessage(`${p2Name} RECYCLING...`, COLORS.p2);
            setTimeout(() => { messageEl.style.display = 'none'; }, 800);
        }

        const cardData = p2Deck.shift();
        p2CardActive = new ActiveCard(cardData, 2, WIDTH - 150 * screenScale, HEIGHT + 100);
        setTimeout(() => { p2CardActive.faceUp = true; }, 100);
        updateStats();
    }

    if (player === 1) {
        p1CardActive.targetX = WIDTH / 2;
        p1CardActive.targetY = HEIGHT / 2 - 20 * screenScale; 
    } else {
        p2CardActive.targetX = WIDTH / 2;
        p2CardActive.targetY = HEIGHT / 2 + 20 * screenScale;
    }

    if (p1CardActive && p2CardActive) {
        gameState = 'CLASH';
        initiateClash();
    }
}

function initiateClash() {
    if (p1CardActive) {
        p1CardActive.opacity = 1;
        p1CardActive.faceUp = true;
    }
    if (p2CardActive) {
        p2CardActive.opacity = 1;
        p2CardActive.faceUp = true;
    }

    p1CardActive.state = 'CLASHING';
    p2CardActive.state = 'CLASHING';
    setTimeout(() => resolveBattle(), 600);
}

function createExplosion(x, y) {
    for (let i = 0; i < 40; i++) {
        particles.push(new Particle(x, y, '#ffffff'));
    }
    for (let i = 0; i < 20; i++) {
        particles.push(new Particle(x, y, '#00f3ff'));
    }
}

function resolveBattle() {
    const c1 = p1CardActive.data;
    const c2 = p2CardActive.data;
    
    if (c1.value === c2.value) {
        isWar = true;
        console.log(`=== WAR INITIATED ===`);
        console.log(`P1 card: ${c1.rank}${c1.suit} (value: ${c1.value}) at position (${p1CardActive.x.toFixed(0)}, ${p1CardActive.y.toFixed(0)})`);
        console.log(`P2 card: ${c2.rank}${c2.suit} (value: ${c2.value}) at position (${p2CardActive.x.toFixed(0)}, ${p2CardActive.y.toFixed(0)})`);
        showMessage("WAR DETECTED!", '#ffff00');
        
        warCards.push({card: c1, owner: 1});
        warCards.push({card: c2, owner: 2});
        console.log(`Added 2 cards to warCards pile. Total war cards: ${warCards.length}`);
        
        p1CardActive.state = 'FADING';
        p2CardActive.state = 'FADING';
        console.log(`Set active cards to FADING state`);
        
        setTimeout(() => {
            console.log(`Clearing active cards before initiating war`);
            p1CardActive = null;
            p2CardActive = null;
            initiateWar();
        }, 500);
        return;
    }

    let winner = 0;
    if (c1.value > c2.value) winner = 1;
    else winner = 2;

    createExplosion(WIDTH / 2, HEIGHT / 2);

    let loserCard = winner === 1 ? p2CardActive : p1CardActive;
    let winnerCard = winner === 1 ? p1CardActive : p2CardActive;

    loserCard.state = 'FADING';
    const offScreenX = winner === 1 ? -200 : WIDTH + 200;
    loserCard.targetX = offScreenX; 

    const winColor = winner === 1 ? COLORS.p1 : COLORS.p2;
    const winnerName = winner === 1 ? p1Name : p2Name;
    showMessage(`${winnerName} OVERRIDE`, winColor);

    if (activeWarCards.length > 0) {
        activeWarCards.forEach(card => {
            card.faceUp = true;
        });
    }

    setTimeout(() => {
        messageEl.style.display = 'none';
        
        if (warCards.length > 0) {
            warCards.forEach(wc => {
                if (winner === 1) {
                    p1Discard.push(wc.card);
                } else {
                    p2Discard.push(wc.card);
                }
            });
            warCards = [];
        }
        
        if (winner === 1) {
            p1Discard.push(c1);
            p1Discard.push(c2);
        } else {
            p2Discard.push(c1);
            p2Discard.push(c2);
        }
        
        if (p1CardActive) p1CardActive.state = 'RESOLVED';
        if (p2CardActive) p2CardActive.state = 'RESOLVED';
        
        activeWarCards.forEach(card => {
            card.state = 'RESOLVED';
        });
        
        gameState = 'WAITING';
        updateStats();
    }, 1000);
}

function initiateWar() {
    console.log(`=== WAR PHASE STARTED ===`);
    console.log(`P1 deck size: ${p1Deck.length}`);
    console.log(`P2 deck size: ${p2Deck.length}`);
    console.log(`Active war cards: ${activeWarCards.length}`);
    showMessage("WAR! 3 FACE-DOWN, 1 FACE-UP", '#ffff00');
    gameState = 'WAR_PHASE_1';
    
    setTimeout(() => {
        console.log(`Calling playWarCards()`);
        playWarCards();
    }, 1500);
}

function playWarCards() {
    console.log(`=== PLAY WAR CARDS STARTED ===`);
    console.log(`Initial state - P1 deck: ${p1Deck.length}, P2 deck: ${p2Deck.length}`);
    console.log(`Previous activeWarCards length: ${activeWarCards.length}`);
    
    if (p1Deck.length === 0 || p2Deck.length === 0) {
        console.log(`No cards left for war! P1: ${p1Deck.length}, P2: ${p2Deck.length}`);
        if (p1Deck.length === 0) {
            endGame(`${p2Name} DOMINATE. ${p1Name} ELIMINATED.`);
        } else {
            endGame(`${p1Name} DOMINATE. ${p2Name} ELIMINATED.`);
        }
        warCards = [];
        activeWarCards = [];
        isWar = false;
        return;
    }

    console.log(`Clearing previous activeWarCards`);
    activeWarCards = [];

    const p1CardsAvailable = p1Deck.length;
    const p2CardsAvailable = p2Deck.length;
    
    const p1FaceDown = Math.min(3, p1CardsAvailable - 1);
    const p2FaceDown = Math.min(3, p2CardsAvailable - 1);
    
    console.log(`P1: ${p1CardsAvailable} cards, playing ${p1FaceDown} face-down + 1 face-up`);
    console.log(`P2: ${p2CardsAvailable} cards, playing ${p2FaceDown} face-down + 1 face-up`);

    const maxFaceDownCards = Math.max(p1FaceDown, p2FaceDown);
    
    for (let i = 0; i < maxFaceDownCards; i++) {
        if (i < p1FaceDown) {
            const p1CardData = p1Deck.shift();
            warCards.push({card: p1CardData, owner: 1});
            
            const p1WarCard = new ActiveCard(p1CardData, 1, 150 * screenScale, HEIGHT + 100);
            p1WarCard.opacity = 1;
            p1WarCard.state = 'ACTIVE';
            p1WarCard.faceUp = false;
            p1WarCard.scale = 0.75;
            
            const offsetX = 45 * screenScale * (p1FaceDown - 1 - i);
            const offsetY = 35 * screenScale * (p1FaceDown - 1 - i);
            p1WarCard.targetX = WIDTH / 2 - 150 * screenScale - offsetX;
            p1WarCard.targetY = HEIGHT / 2 - 80 * screenScale - offsetY;
            
            console.log(`Created P1 face-down war card ${i}: target (${p1WarCard.targetX.toFixed(0)}, ${p1WarCard.targetY.toFixed(0)})`);
            console.log(`  Start pos: (${p1WarCard.x.toFixed(0)}, ${p1WarCard.y.toFixed(0)})`);
            
            activeWarCards.push(p1WarCard);
        }
        
        if (i < p2FaceDown) {
            const p2CardData = p2Deck.shift();
            warCards.push({card: p2CardData, owner: 2});
            
            const p2WarCard = new ActiveCard(p2CardData, 2, WIDTH - 150 * screenScale, HEIGHT + 100);
            p2WarCard.opacity = 1;
            p2WarCard.state = 'ACTIVE';
            p2WarCard.faceUp = false;
            p2WarCard.scale = 0.75;
            
            const offsetX = 45 * screenScale * (p2FaceDown - 1 - i);
            const offsetY = 35 * screenScale * (p2FaceDown - 1 - i);
            p2WarCard.targetX = WIDTH / 2 + 150 * screenScale + offsetX;
            p2WarCard.targetY = HEIGHT / 2 + 80 * screenScale + offsetY;
            
            console.log(`Created P2 face-down war card ${i}: target (${p2WarCard.targetX.toFixed(0)}, ${p2WarCard.targetY.toFixed(0)})`);
            console.log(`  Start pos: (${p2WarCard.x.toFixed(0)}, ${p2WarCard.y.toFixed(0)})`);
            
            activeWarCards.push(p2WarCard);
        }
    }
    
    console.log(`Total war cards created: ${activeWarCards.length}`);
    console.log(`Active war cards array length: ${activeWarCards.length}`);

    updateStats();

    setTimeout(() => {
        console.log(`=== CREATING TIE-BREAKER CARDS ===`);
        console.log(`Active war cards before tie-breaker: ${activeWarCards.length}`);
        
        const p1CardData = p1Deck.shift();
        const p2CardData = p2Deck.shift();
        
        console.log(`P1 tie-breaker: ${p1CardData.rank}${p1CardData.suit}`);
        console.log(`P2 tie-breaker: ${p2CardData.rank}${p2CardData.suit}`);
        
        p1CardActive = new ActiveCard(p1CardData, 1, 150 * screenScale, HEIGHT + 100);
        p2CardActive = new ActiveCard(p2CardData, 2, WIDTH - 150 * screenScale, HEIGHT + 100);
        
        p1CardActive.opacity = 1;
        p2CardActive.opacity = 1;
        p1CardActive.state = 'ACTIVE';
        p2CardActive.state = 'ACTIVE';
        
        p1CardActive.faceUp = true; 
        p2CardActive.faceUp = true; 
        
        p1CardActive.targetX = WIDTH / 2 - 50 * screenScale;
        p1CardActive.targetY = HEIGHT / 2 - 20 * screenScale;
        p2CardActive.targetX = WIDTH / 2 + 50 * screenScale;
        p2CardActive.targetY = HEIGHT / 2 + 20 * screenScale;
        
        console.log(`Tie-breaker positions - P1: (${p1CardActive.x.toFixed(0)}, ${p1CardActive.y.toFixed(0)}) -> (${p1CardActive.targetX.toFixed(0)}, ${p1CardActive.targetY.toFixed(0)})`);
        console.log(`Tie-breaker positions - P2: (${p2CardActive.x.toFixed(0)}, ${p2CardActive.y.toFixed(0)}) -> (${p2CardActive.targetX.toFixed(0)}, ${p2CardActive.targetY.toFixed(0)})`);
        
        updateStats();
        
        setTimeout(() => {
            console.log(`Initiating clash after tie-breaker cards positioned`);
            gameState = 'CLASH';
            initiateClash();
        }, 600);
    }, 800);
}

function update() {
    circuitryOffset -= 0.5;
    if (p1CardActive) p1CardActive.update();
    if (p2CardActive) p2CardActive.update();
    
    if (activeWarCards.length > 0) {
        for (let i = activeWarCards.length - 1; i >= 0; i--) {
            const card = activeWarCards[i];
            card.update();
            if (card.opacity <= 0) {
                activeWarCards.splice(i, 1);
            }
        }
    }

    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        if (particles[i].alpha <= 0) {
            particles.splice(i, 1);
        }
    }
}

function drawBackground() {
    const centerX = WIDTH / 2;
    const centerY = HEIGHT / 2;
    const tableW = Math.min(WIDTH * 0.8, 800);
    const tableH = Math.min(HEIGHT * 0.6, 500);

    ctx.save();
    ctx.translate(centerX, centerY);
    
    ctx.shadowColor = COLORS.p1;
    ctx.shadowBlur = 20;
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 2;
    ctx.strokeRect(-tableW/2, -tableH/2, tableW, tableH);
    ctx.shadowBlur = 0;

    ctx.beginPath();
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    for(let i = -tableW/2; i < tableW/2; i+=40) {
        ctx.moveTo(i, -tableH/2);
        ctx.lineTo(i, tableH/2);
    }
    for(let i = -tableH/2; i < tableH/2; i+=40) {
        ctx.moveTo(-tableW/2, i);
        ctx.lineTo(tableW/2, i);
    }
    ctx.stroke();
    ctx.restore();

    tableJunk.forEach(j => {
        ctx.save();
        ctx.translate(j.x, j.y);
        ctx.rotate(j.rot);
        ctx.fillStyle = j.color;
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 2;
        
        if (j.type === 'rect') {
            ctx.fillRect(-j.w/2, -j.h/2, j.w, j.h);
            ctx.strokeRect(-j.w/2, -j.h/2, j.w, j.h);
        } else {
            ctx.beginPath();
            ctx.rect(-j.w/2, -j.h/2, j.w, j.h);
            ctx.fill();
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(-j.w/2 - 5, 0);
            ctx.lineTo(j.w/2 + 5, 0);
            ctx.stroke();
        }
        ctx.restore();
    });
}

function drawCircuitry() {
    ctx.save();
    ctx.strokeStyle = COLORS.circuit;
    ctx.lineWidth = 2;
    ctx.setLineDash([10, 15]);
    ctx.lineDashOffset = circuitryOffset;
    
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(150, 100);
    ctx.lineTo(150, HEIGHT - 520);
    ctx.stroke();

    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 85, 0, 0.4)';
    ctx.moveTo(WIDTH, 0);
    ctx.lineTo(WIDTH - 150, 100);
    ctx.lineTo(WIDTH - 150, HEIGHT - 520);
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.strokeStyle = COLORS.p1;
    ctx.strokeRect(10, 10, 50, 50);
    ctx.strokeStyle = COLORS.p2;
    ctx.strokeRect(WIDTH - 60, 10, 50, 50);
    
    ctx.restore();
}

function draw() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    
    drawBackground();
    drawCircuitry();

    const p1DeckX = 150 * screenScale;
    const p1DeckY = HEIGHT - 520 * screenScale;
    const p1DiscardX = 150 * screenScale;
    const p1DiscardY = HEIGHT - 220 * screenScale;

    const p2DeckX = WIDTH - 150 * screenScale;
    const p2DeckY = HEIGHT - 520 * screenScale;
    const p2DiscardX = WIDTH - 150 * screenScale;
    const p2DiscardY = HEIGHT - 220 * screenScale;

    drawPile(p1DeckX, p1DeckY, p1Deck.length, "BUFFER", COLORS.p1, p1Deck.length > 0 ? true : false);
    drawPile(p1DiscardX, p1DiscardY, p1Discard.length, "RECURRABLE", '#ffffff', true);
    
    drawPile(p2DeckX, p2DeckY, p2Deck.length, "BUFFER", COLORS.p2, p2Deck.length > 0 ? true : false);
    drawPile(p2DiscardX, p2DiscardY, p2Discard.length, "RECURRABLE", '#ffffff', true);

    activeWarCards.forEach((card, index) => {
        card.draw(ctx);
    });
    
    if (p1CardActive) p1CardActive.draw(ctx);
    if (p2CardActive) p2CardActive.draw(ctx);
    
    particles.forEach(p => p.draw(ctx));
}

function drawPile(x, y, count, label, color, active) {
    ctx.save();
    ctx.translate(x, y);
    
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 5;
    ctx.font = '14px "Courier New", monospace';
    ctx.textAlign = 'center';
    ctx.fillText(label, 0, -CARD_H/2 - 15);
    ctx.shadowBlur = 0;

    if (count > 0) {
        const visible = Math.min(count, 5);
        for(let i=0; i<visible; i++) {
            ctx.fillStyle = active ? 'rgba(2, 4, 8, 0.9)' : 'rgba(2, 4, 8, 0.3)';
            ctx.strokeStyle = active ? color : 'rgba(255,255,255,0.1)';
            ctx.lineWidth = 2;
            ctx.strokeRect(-CARD_W/2 - i, -CARD_H/2 - i, CARD_W, CARD_H);
            ctx.fillRect(-CARD_W/2 - i, -CARD_H/2 - i, CARD_W, CARD_H);
            
            if (i === 0) {
                 ctx.fillStyle = active ? color : '#555';
                 ctx.globalAlpha = 0.2;
                 ctx.fillRect(-CARD_W/2 + 20, -10, CARD_W - 40, 20);
                 ctx.globalAlpha = 1.0;
            }
        }
        
        ctx.fillStyle = '#000';
        ctx.fillRect(-20, -15, 40, 30);
        ctx.fillStyle = active ? color : '#fff';
        ctx.font = 'bold 16px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count, 0, 0);
    } else {
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(-CARD_W/2, -CARD_H/2, CARD_W, CARD_H);
    }
    ctx.restore();
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

window.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'z') playCard(1);
    if (e.key.toLowerCase() === 'm') playCard(2);
});

window.addEventListener('resize', resize);

debugBtn.addEventListener('click', async () => {
    await initGameDebug(5);
});

initializeBtn.addEventListener('click', async () => {
    if (gameInitialized) return;
    
    p1Name = p1NameInput.value.toUpperCase() || 'DRIFTERS';
    p2Name = p2NameInput.value.toUpperCase() || 'SCAVS';
    
    p1ControlsNameEl.textContent = p1Name;
    p2ControlsNameEl.textContent = p2Name;
    
    initializeBtn.textContent = 'SEQUENCING';
    initializeBtn.disabled = true;
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    startMenu.classList.add('hidden');
    gameInitialized = true;
    
    resize();
    generateJunk();
    await initGame();
    loop();
});
</script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
