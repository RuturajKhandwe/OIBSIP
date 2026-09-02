/**
 * ChatFlow Real-Time Multi-Room Client Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current Active Application State
    const state = {
        currentRoom: 'General',
        currentUsername: document.getElementById('currentUsername')?.textContent.trim() || '',
        socket: null,
        notificationsAllowed: false,
        onlineUsers: [],
        allRooms: []
    };

    // DOM Elements
    const elements = {
        connectionBadge: document.getElementById('connectionBadge'),
        connectionText: document.getElementById('connectionText'),
        roomList: document.getElementById('roomList'),
        roomSearchInput: document.getElementById('roomSearchInput'),
        currentRoomTitle: document.getElementById('currentRoomTitle'),
        roomOnlineBadge: document.getElementById('roomOnlineBadge'),
        messagesContainer: document.getElementById('messagesContainer'),
        messagesFeed: document.getElementById('messagesFeed'),
        messagesEmpty: document.getElementById('messagesEmpty'),
        messageForm: document.getElementById('messageForm'),
        messageInput: document.getElementById('messageInput'),
        openCreateRoomBtn: document.getElementById('openCreateRoomBtn'),
        createRoomModal: document.getElementById('createRoomModal'),
        createRoomForm: document.getElementById('createRoomForm'),
        newRoomNameInput: document.getElementById('newRoomNameInput'),
        cancelCreateRoomBtn: document.getElementById('cancelCreateRoomBtn'),
        togglePresenceBtn: document.getElementById('togglePresenceBtn'),
        presenceCountText: document.getElementById('presenceCountText'),
        presenceDrawer: document.getElementById('presenceDrawer'),
        presenceList: document.getElementById('presenceList'),
        notificationBanner: document.getElementById('notificationBanner'),
        enableNotificationsBtn: document.getElementById('enableNotificationsBtn'),
        dismissNotificationsBtn: document.getElementById('dismissNotificationsBtn'),
        toastContainer: document.getElementById('toastContainer'),
        sidebarToggleBtn: document.getElementById('sidebarToggleBtn'),
        chatSidebar: document.getElementById('chatSidebar')
    };

    // Initialize Notification Check & Socket Setup
    initNotificationCheck();
    initSocketConnection();
    attachEventListeners();

    /* ==========================================================================
       Socket.IO Connection & Events
       ========================================================================== */

    function initSocketConnection() {
        state.socket = io({
            reconnectionAttempts: 5,
            timeout: 10000
        });

        state.socket.on('connect', () => {
            updateConnectionStatus(true, 'Connected');
            showToast('Connected to ChatFlow workspace', 'info');
            joinRoom(state.currentRoom);
        });

        state.socket.on('disconnect', () => {
            updateConnectionStatus(false, 'Disconnected');
            showToast('Disconnected from server. Reconnecting...', 'error');
        });

        state.socket.on('connect_error', () => {
            updateConnectionStatus(false, 'Connection Error');
        });

        state.socket.on('room_list', handleRoomList);
        state.socket.on('message_history', handleMessageHistory);
        state.socket.on('receive_message', handleReceiveMessage);
        state.socket.on('system_message', handleSystemMessage);
        state.socket.on('presence_update', handlePresenceUpdate);
        state.socket.on('error', handleErrorEvent);
    }

    /* ==========================================================================
       Socket Event Handlers
       ========================================================================== */

    function handleRoomList(rooms) {
        state.allRooms = rooms || [];
        renderRooms(state.allRooms);
    }

    function renderRooms(rooms) {
        if (!elements.roomList) return;
        elements.roomList.innerHTML = '';

        const searchTerm = (elements.roomSearchInput?.value || '').toLowerCase().trim();
        const filteredRooms = rooms.filter(r => r.name.toLowerCase().includes(searchTerm));

        if (!filteredRooms || filteredRooms.length === 0) {
            elements.roomList.innerHTML = '<div class="room-item-placeholder">No matching rooms</div>';
            return;
        }

        filteredRooms.forEach(room => {
            const item = document.createElement('div');
            item.className = `room-item ${room.name === state.currentRoom ? 'active' : ''}`;
            item.dataset.roomName = room.name;

            const nameSpan = document.createElement('div');
            nameSpan.className = 'room-item-name';
            nameSpan.innerHTML = `<span class="room-hash">#</span><span>${room.name}</span>`;

            const badge = document.createElement('span');
            badge.className = 'online-badge';
            badge.textContent = `${room.online_count || 0}`;

            item.appendChild(nameSpan);
            item.appendChild(badge);

            item.addEventListener('click', () => {
                if (room.name !== state.currentRoom) {
                    joinRoom(room.name);
                }
            });

            elements.roomList.appendChild(item);
        });
    }

    function handleMessageHistory(data) {
        if (data.room_name !== state.currentRoom) return;

        elements.messagesFeed.innerHTML = '';
        const messages = data.messages || [];

        if (messages.length === 0) {
            elements.messagesEmpty.classList.remove('hidden');
        } else {
            elements.messagesEmpty.classList.add('hidden');
            messages.forEach(msg => appendMessageBubble(msg));
        }

        scrollToBottom();
    }

    function handleReceiveMessage(msg) {
        if (msg.room_name !== state.currentRoom) return;

        elements.messagesEmpty.classList.add('hidden');
        appendMessageBubble(msg);
        scrollToBottom();

        if (msg.sender !== state.currentUsername) {
            triggerDesktopNotification(msg);
        }
    }

    function handleSystemMessage(data) {
        if (data.room_name !== state.currentRoom) return;

        elements.messagesEmpty.classList.add('hidden');
        
        const sysDiv = document.createElement('div');
        sysDiv.className = 'msg-system';
        sysDiv.textContent = `── ${data.content} ──`;
        
        elements.messagesFeed.appendChild(sysDiv);
        scrollToBottom();
    }

    function handlePresenceUpdate(data) {
        if (data.room_name !== state.currentRoom) return;

        state.onlineUsers = data.online_users || [];
        const count = data.count || state.onlineUsers.length;

        if (elements.presenceCountText) elements.presenceCountText.textContent = count;
        if (elements.roomOnlineBadge) elements.roomOnlineBadge.textContent = `${count} active member${count === 1 ? '' : 's'}`;

        if (elements.presenceList) {
            elements.presenceList.innerHTML = '';
            state.onlineUsers.forEach(username => {
                const li = document.createElement('li');
                li.className = 'presence-user';
                
                const dot = document.createElement('span');
                dot.className = 'presence-user-dot';
                
                const name = document.createElement('span');
                name.textContent = username;
                if (username === state.currentUsername) {
                    name.textContent += ' (You)';
                    name.style.fontWeight = '600';
                }

                li.appendChild(dot);
                li.appendChild(name);
                elements.presenceList.appendChild(li);
            });
        }
    }

    function handleErrorEvent(data) {
        const errorMsg = data.message || 'An error occurred';
        showToast(errorMsg, 'error');
    }

    /* ==========================================================================
       UI Actions & Helpers
       ========================================================================== */

    function joinRoom(roomName) {
        state.currentRoom = roomName;
        elements.currentRoomTitle.textContent = `# ${roomName}`;

        const roomItems = elements.roomList.querySelectorAll('.room-item');
        roomItems.forEach(item => {
            if (item.dataset.roomName === roomName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        if (elements.chatSidebar) {
            elements.chatSidebar.classList.remove('active');
        }

        state.socket.emit('join_room', { room_name: roomName });
    }

    function appendMessageBubble(msg) {
        const isOutgoing = msg.sender === state.currentUsername;
        
        const wrapper = document.createElement('div');
        wrapper.className = `msg-wrapper ${isOutgoing ? 'outgoing' : 'incoming'}`;

        // Initial Avatar
        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.textContent = (msg.sender && msg.sender.length > 0) ? msg.sender[0].toUpperCase() : 'U';

        const bodyCol = document.createElement('div');
        bodyCol.className = 'msg-body-col';

        const meta = document.createElement('div');
        meta.className = 'msg-meta';
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'msg-sender';
        senderSpan.textContent = msg.sender;

        const timeSpan = document.createElement('span');
        timeSpan.className = 'msg-time';
        timeSpan.textContent = formatTimestamp(msg.timestamp);

        meta.appendChild(senderSpan);
        meta.appendChild(document.createTextNode(' · '));
        meta.appendChild(timeSpan);

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';
        bubble.innerHTML = msg.content;

        bodyCol.appendChild(meta);
        bodyCol.appendChild(bubble);

        wrapper.appendChild(avatar);
        wrapper.appendChild(bodyCol);

        elements.messagesFeed.appendChild(wrapper);
    }

    function attachEventListeners() {
        // Search Filter for Rooms
        if (elements.roomSearchInput) {
            elements.roomSearchInput.addEventListener('input', () => {
                renderRooms(state.allRooms);
            });
        }

        // Message Submit Form
        if (elements.messageForm) {
            elements.messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const content = elements.messageInput.value.trim();
                if (!content) return;

                state.socket.emit('send_message', {
                    room_name: state.currentRoom,
                    content: content
                });

                elements.messageInput.value = '';
                elements.messageInput.focus();
            });
        }

        // Emoji Toolbar Buttons
        document.querySelectorAll('.emoji-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const shortcode = btn.dataset.emoji;
                elements.messageInput.value += (elements.messageInput.value ? ' ' : '') + shortcode;
                elements.messageInput.focus();
            });
        });

        // Create Room Toggle & Form Submit
        if (elements.openCreateRoomBtn) {
            elements.openCreateRoomBtn.addEventListener('click', () => {
                elements.createRoomModal.classList.toggle('hidden');
                if (!elements.createRoomModal.classList.contains('hidden')) {
                    elements.newRoomNameInput.focus();
                }
            });
        }

        if (elements.cancelCreateRoomBtn) {
            elements.cancelCreateRoomBtn.addEventListener('click', () => {
                elements.createRoomModal.classList.add('hidden');
            });
        }

        if (elements.createRoomForm) {
            elements.createRoomForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const roomName = elements.newRoomNameInput.value.trim();
                if (!roomName) return;

                state.socket.emit('create_room', { room_name: roomName });
                elements.newRoomNameInput.value = '';
                elements.createRoomModal.classList.add('hidden');
            });
        }

        // Presence Drawer Toggle
        if (elements.togglePresenceBtn) {
            elements.togglePresenceBtn.addEventListener('click', () => {
                elements.presenceDrawer.classList.toggle('hidden');
            });
        }

        // Mobile Sidebar Toggle
        if (elements.sidebarToggleBtn) {
            elements.sidebarToggleBtn.addEventListener('click', () => {
                elements.chatSidebar.classList.toggle('active');
            });
        }
    }

    /* ==========================================================================
       Notification & Toast Utilities
       ========================================================================== */

    function initNotificationCheck() {
        if (!("Notification" in window)) return;

        if (Notification.permission === 'granted') {
            state.notificationsAllowed = true;
        } else if (Notification.permission !== 'denied') {
            if (elements.notificationBanner) {
                elements.notificationBanner.classList.remove('hidden');

                elements.enableNotificationsBtn?.addEventListener('click', () => {
                    Notification.requestPermission().then(permission => {
                        if (permission === 'granted') {
                            state.notificationsAllowed = true;
                            showToast('Desktop notifications enabled!', 'info');
                        }
                        elements.notificationBanner.classList.add('hidden');
                    });
                });

                elements.dismissNotificationsBtn?.addEventListener('click', () => {
                    elements.notificationBanner.classList.add('hidden');
                });
            }
        }
    }

    function triggerDesktopNotification(msg) {
        if (!state.notificationsAllowed || !document.hidden) return;

        try {
            const title = `New message from ${msg.sender} (#${msg.room_name})`;
            const options = {
                body: msg.content.replace(/<[^>]*>?/gm, ''),
                icon: '💬'
            };
            new Notification(title, options);
        } catch (e) {
            console.warn('Desktop Notification error:', e);
        }
    }

    function updateConnectionStatus(connected, text) {
        if (!elements.connectionBadge) return;
        elements.connectionText.textContent = text;
        if (connected) {
            elements.connectionBadge.className = 'status-badge status-connected';
        } else {
            elements.connectionBadge.className = 'status-badge status-disconnected';
        }
    }

    function formatTimestamp(ts) {
        if (!ts) return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        try {
            const date = new Date(ts);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return ts;
        }
    }

    function scrollToBottom() {
        if (elements.messagesContainer) {
            elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
        }
    }

    function showToast(message, type = 'info') {
        if (!elements.toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
