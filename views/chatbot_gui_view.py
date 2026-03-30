# views/chatbot_gui_view.py
"""
ChatbotGUIView - Persistent floating AI Assistant panel for all pages.

add_floating_chat() is called by GUITheme.applyTheming() on every page.
It returns the drawer so the caller can wire a toggle button to it.
"""

import asyncio
from nicegui import ui, app


class ChatbotGUIView:
    _chatbot_controller = None

    @staticmethod
    def add_floating_chat():
        """
        Builds the left-side chat drawer and injects required CSS.
        Returns the drawer element so the caller can toggle it.
        """
        ui.add_head_html('''
        <style>
            /* Styles for the AI chat drawer panel: backgrounds, chat bubbles,
               header/footer borders, input overrides, and typing animation. */

            /* ── Drawer background: white in light mode, dark grey in dark mode ── */
            .ai-drawer { background: #ffffff !important; }
            .body--dark .ai-drawer { background: #1e1e1e !important; }

            /* ── Bubble rows: user messages align right, AI messages align left ── */
            .bubble-row-user {
                display: flex;
                justify-content: flex-end;  /* push user bubble to right edge */
                width: 100%;
            }
            .bubble-row-ai {
                display: flex;
                justify-content: flex-start;  /* keep AI bubble at left edge */
                width: 100%;
            }

            /* ── User chat bubble: dark background, rounded except bottom-right ── */
            .user-bubble {
                display: inline-block;
                background: #1a1a1a;
                color: #ffffff;
                border-radius: 16px 16px 4px 16px;  /* flat bottom-right = "sent" look */
                padding: 10px 16px;
                max-width: 85%;
                font-size: 0.95rem;
                line-height: 1.5;
                word-break: break-word;
                white-space: pre-wrap;  /* preserve newlines in AI output */
            }
            /* Dark mode inverts user bubble to light grey */
            .body--dark .user-bubble { background: #e0e0e0; color: #000000; }

            /* ── AI chat bubble: light background, rounded except bottom-left ── */
            .ai-bubble {
                display: inline-block;
                background: #f0f0f0;
                color: #111111;
                border-radius: 16px 16px 16px 4px;  /* flat bottom-left = "received" look */
                padding: 10px 16px;
                max-width: 85%;
                font-size: 0.95rem;
                line-height: 1.5;
                word-break: break-word;
                white-space: pre-wrap;
            }
            .body--dark .ai-bubble { background: #2d2d2d; color: #f0f0f0; }

            /* ── Small label shown above each AI bubble ── */
            .ai-name { font-size: 0.7rem; color: #888; margin-bottom: 2px; margin-left: 2px; }
            .body--dark .ai-name { color: #aaa; }

            /* ── Thin separator lines between header/messages and messages/input ── */
            .ai-header  { border-bottom: 1px solid rgba(128,128,128,0.25); flex-shrink: 0; }
            .ai-input-bar { border-top: 1px solid rgba(128,128,128,0.25); flex-shrink: 0; }

            /* ── Override Quasar input field colors inside the chat panel (dark mode) ── */
            .body--dark .ai-input .q-field__control { background: #2a2a2a !important; }
            .body--dark .ai-input .q-field__native   { color: #f0f0f0    !important; }
            .body--dark .ai-input .q-field__label    { color: #aaa       !important; }
            .body--dark .ai-input .q-field__outline  { border-color: rgba(255,255,255,0.2) !important; }

            /* ── Animated dots shown while the AI is thinking ── */
            .typing-dot {
                display: inline-block; width: 6px; height: 6px;
                border-radius: 50%; background: #aaa;
                animation: tdot 1.2s infinite; margin: 0 2px;
            }
            /* Stagger each dot's fade so they pulse in sequence */
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            /* Keyframes: mostly invisible, peak opacity at 40% of the cycle */
            @keyframes tdot { 0%,80%,100%{opacity:0.2} 40%{opacity:1} }
        </style>
        ''')

        with ui.left_drawer(value=False, bordered=True, top_corner=True, bottom_corner=True) \
                .style('width: 25vw; min-width: 340px; padding: 0; display: flex; flex-direction: column;') \
                .classes('ai-drawer') as drawer:

            # Header
            with ui.row().classes('w-full items-center justify-between px-4 py-3 ai-header'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('smart_toy').classes('!text-black dark:!text-white')
                    ui.label('AI Assistant').classes('font-bold text-lg !text-black dark:!text-white')
                def _close():
                    drawer.hide()
                    app.storage.user['chat_open'] = False
                    app.storage.user['chat_history'] = []

                def _export():
                    ctrl = ChatbotGUIView._chatbot_controller
                    if ctrl is None:
                        ui.notify('No configuration loaded.', type='warning')
                        return
                    ok = ctrl.save_config()
                    if ok:
                        ui.notify('Configuration saved to disk.', type='positive')
                    else:
                        ui.notify('Failed to save configuration.', type='negative')

                with ui.row().classes('items-center gap-1'):
                    ui.button('Export to Config', icon='save') \
                        .props('flat dense') \
                        .classes('text-xs !text-black dark:!text-white') \
                        .on('click', _export)
                    ui.button(icon='close') \
                        .props('flat round dense') \
                        .classes('!text-black dark:!text-white') \
                        .on('click', _close)

            # Messages
            scroll = ui.scroll_area().style('flex: 1; min-height: 0; height: calc(100vh - 140px);')
            with scroll:
                chat_column = ui.column().classes('w-full gap-3 p-4')
                history = app.storage.user.get('chat_history', [])
                if not history:
                    with chat_column:
                        ui.html(sanitize=False,
                                content='<!-- Initial greeting bubble shown when chat history is empty -->'
                                        '<div class="ai-name">AI Assistant</div>'
                                        '<div class="bubble-row-ai"><div class="ai-bubble">How may I assist you?</div></div>')
                else:
                    for msg in history:
                        with chat_column:
                            if msg['role'] == 'user':
                                ui.html(sanitize=False,
                                        content=f'<!-- User message bubble, right-aligned -->'
                                                f'<div class="bubble-row-user"><div class="user-bubble">{msg["content"]}</div></div>').classes('w-full')
                            else:
                                ui.html(sanitize=False,
                                        content=f'<!-- AI response bubble with sender label, left-aligned -->'
                                                f'<div class="ai-name">AI Assistant</div>'
                                                f'<div class="bubble-row-ai"><div class="ai-bubble">{msg["content"]}</div></div>')

            # Typing indicator
            with ui.row().classes('px-4').style('min-height: 26px; flex-shrink: 0;'):
                typing = ui.html(sanitize=False, content='').classes('text-sm')

            # Input bar
            with ui.row().classes('w-full items-center gap-2 px-3 py-3 ai-input-bar'):
                query_input = ui.input(placeholder='Message AI Assistant...') \
                    .classes('flex-1 ai-input').props('outlined dense')
                send_btn = ui.button(icon='send') \
                    .props('round dense') \
                    .classes('!bg-black dark:!bg-white !text-white dark:!text-black') \
                    .style('flex-shrink: 0;')

                async def send():
                    query = query_input.value.strip()
                    if not query:
                        return
                    ctrl = ChatbotGUIView._chatbot_controller
                    if ctrl is None:
                        ui.notify('Load a configuration first.', type='warning')
                        return
                    history = app.storage.user.setdefault('chat_history', [])
                    is_first_message = len(history) == 0
                    history.append({'role': 'user', 'content': query})
                    with chat_column:
                        ui.html(sanitize=False,
                                content=f'<!-- Newly sent user message bubble -->'
                                        f'<div class="bubble-row-user"><div class="user-bubble">{query}</div></div>').classes('w-full')
                    scroll.scroll_to(percent=1)
                    query_input.set_value('')
                    send_btn.disable()
                    if is_first_message:
                        typing.set_content(
                            '<span style="color:#ccc;font-size:0.78rem;">message sending...</span>'
                        )
                        await asyncio.sleep(0.6)
                    typing.set_content(
                        '<span style="color:#aaa;font-size:0.78rem;margin-right:4px;">thinking</span>'
                        '<span class="typing-dot"></span>'
                        '<span class="typing-dot"></span>'
                        '<span class="typing-dot"></span>'
                    )
                    try:
                        prior = history[:-1]  # all turns before the one just appended
                        response = await ctrl.chat(query, history=prior)
                    except Exception as e:
                        response = f'Error: {e}'
                    finally:
                        typing.set_content('')
                        send_btn.enable()
                    history.append({'role': 'ai', 'content': response})
                    with chat_column:
                        ui.html(sanitize=False,
                                content=f'<!-- AI response bubble appended after reply arrives -->'
                                        f'<div class="ai-name">AI Assistant</div>'
                                        f'<div class="bubble-row-ai"><div class="ai-bubble">{response}</div></div>')
                    await asyncio.sleep(0.05)
                    scroll.scroll_to(percent=1)

                send_btn.on('click', send)
                query_input.on('keyup.enter', send)

        return drawer