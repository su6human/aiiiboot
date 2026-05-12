document.addEventListener('DOMContentLoaded', () => {
    console.log("Digital Twin App Started");

    const API_BASE = window.location.origin;

    // --- Selectors ---
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.page-section');
    const sessionsList = document.getElementById('sessions-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-chat');
    const apiKeyInput = document.getElementById('groq-api-key');

    // --- State ---
    let sessions = [];
    let activeSessionId = null;
    let chatMessages = [];

    // --- Navigation ---
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            if (!targetId) return;

            navButtons.forEach(b => b.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            btn.classList.add('active');
            const targetSection = document.getElementById(targetId);
            if (targetSection) targetSection.classList.add('active');

            if (targetId === 'radar') renderRadarChart();
        });
    });

    // --- Session Management ---
    function renderSessions() {
        if (!sessionsList) return;
        sessionsList.innerHTML = '';
        sessions.forEach(s => {
            const div = document.createElement('div');
            div.className = `session-item ${s.id === activeSessionId ? 'active' : ''}`;
            div.textContent = s.title || 'Новый чат';
            div.onclick = () => switchSession(s.id);
            sessionsList.appendChild(div);
        });
    }

    function switchSession(id) {
        console.log("Switching to session:", id);
        activeSessionId = id;
        const session = sessions.find(s => s.id === id);
        chatMessages = session ? session.messages : [];
        renderChat();
        renderSessions();
    }

    async function createNewChat() {
        console.log("Creating new chat...");
        try {
            if (newChatBtn) newChatBtn.disabled = true;
            const res = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' });
            if (!res.ok) throw new Error("Failed to create session on server");
            
            const newSession = await res.json();
            sessions.unshift(newSession);
            switchSession(newSession.id);
        } catch (e) {
            console.error("Create Chat Error:", e);
            alert("Не удалось создать новый чат. Проверь соединение с сервером.");
        } finally {
            if (newChatBtn) newChatBtn.disabled = false;
        }
    }

    if (newChatBtn) newChatBtn.addEventListener('click', createNewChat);

    // --- Chat Rendering ---
    function renderChat() {
        if (!chatBox) return;
        chatBox.innerHTML = '';

        if (chatMessages.length === 0) {
            const welcome = document.createElement('div');
            welcome.className = 'chat-message msg-assistant';
            welcome.innerHTML = '<div class="msg-header">🤖 Digital Twin Coach</div><div>Привет, Актан! О чем сегодня поговорим? Я готов помочь с планом обучения или разобрать твои навыки.</div>';
            chatBox.appendChild(welcome);
        } else {
            chatMessages.forEach(msg => {
                const div = document.createElement('div');
                div.className = `chat-message ${msg.role === 'user' ? 'msg-user' : 'msg-assistant'}`;
                const header = msg.role === 'user' ? '👤 Актан' : '🤖 Digital Twin Coach';
                
                let text = msg.content
                    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                    .replace(/\*(.*?)\*/g, '<i>$1</i>')
                    .replace(/\n/g, '<br>');

                div.innerHTML = `<div class="msg-header">${header}</div><div>${text}</div>`;
                chatBox.appendChild(div);
            });
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        const apiKey = apiKeyInput ? apiKeyInput.value.trim() : '';

        if (!text) return;
        if (!apiKey) {
            alert("⚠️ Введи Groq API Key в панели слева!");
            return;
        }

        if (!activeSessionId) {
            await createNewChat();
        }

        // UI Update
        chatMessages.push({ role: 'user', content: text });
        chatInput.value = '';
        renderChat();

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-message msg-assistant';
        loadingDiv.innerHTML = '<i>Думаю...</i>';
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: chatMessages,
                    api_key: apiKey,
                    session_id: activeSessionId
                })
            });

            const data = await res.json();
            chatBox.removeChild(loadingDiv);

            if (res.ok) {
                chatMessages.push({ role: 'assistant', content: data.response });
                // Update session title locally if it was the first message
                const currentSession = sessions.find(s => s.id === activeSessionId);
                if (currentSession && currentSession.messages.length <= 2) {
                    currentSession.title = text.substring(0, 20) + "...";
                    renderSessions();
                }
            } else {
                chatMessages.push({ role: 'assistant', content: `❌ Ошибка: ${data.detail}` });
            }
        } catch (e) {
            if (loadingDiv.parentNode) chatBox.removeChild(loadingDiv);
            chatMessages.push({ role: 'assistant', content: `❌ Ошибка сети.` });
        }
        renderChat();
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (chatInput) chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // --- Init ---
    async function init() {
        try {
            const res = await fetch(`${API_BASE}/api/history`);
            const data = await res.json();
            sessions = data.sessions || [];
            if (sessions.length > 0) {
                switchSession(sessions[0].id);
            } else {
                createNewChat();
            }
        } catch (e) {
            console.error("Init History Error:", e);
            createNewChat(); // Attempt to create at least one if fetch fails
        }
    }

    init();
    loadPredictionData(); // Call existing functions fromTurn 25 if they exist
    
    // --- Re-adding Missing Functions ---
    async function loadPredictionData() {
        const homeTopJob = document.getElementById('home-top-job');
        const predictionGrid = document.getElementById('prediction-grid');
        try {
            const res = await fetch(`${API_BASE}/api/prediction`);
            const data = await res.json();
            if (homeTopJob && data.top_3_jobs && data.top_3_jobs[0]) {
                homeTopJob.innerHTML = `<h2 class="job-title">🎮 ${data.top_3_jobs[0].title}</h2><p class="job-match">⚡ Совпадение: ${data.top_3_jobs[0].match_percent}%</p>`;
            }
            if (predictionGrid && data.top_3_jobs) {
                predictionGrid.innerHTML = data.top_3_jobs.map((j, i) => `<div class="job-card"><h3>#${i+1} ${j.title}</h3><h2>${j.match_percent}%</h2></div>`).join('');
            }
        } catch(e) {}
    }

    let radarLoaded = false;
    async function renderRadarChart() {
        if (radarLoaded) return;
        try {
            const res = await fetch(`${API_BASE}/api/skills`);
            const data = await res.json();
            const traces = [
                { type: 'scatterpolar', r: [...data.hard_skills, data.hard_skills[0]], theta: [...data.categories, data.categories[0]], fill: 'toself', name: 'Hard' },
                { type: 'scatterpolar', r: [...data.soft_skills, data.soft_skills[0]], theta: [...data.categories, data.categories[0]], fill: 'toself', name: 'Soft' }
            ];
            Plotly.newPlot('radar-chart', traces, { polar: { radialaxis: { visible: true, range: [0, 100] } }, paper_bgcolor: 'rgba(0,0,0,0)', font: { color: 'white' } });
            radarLoaded = true;
        } catch(e) {}
    }
});
